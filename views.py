""" 

"""

from lxml import etree
from utils import *
from django.shortcuts import render_to_response
from django.utils import simplejson
import settings # app local
import dateutil.parser

NS = 'http://indivo.org/vocab/xml/documents#'

LAB_STATUSES = {
    'correction': 'Correction',
    'preliminary': 'Preliminary',
    'final': 'Final',
}

def start_auth(request):
    """
    begin the oAuth protocol with the server
    
    expects either a record_id or carenet_id parameter,
    now that we are carenet-aware
    """
    # create the client to Indivo
    client = get_indivo_client(request, with_session_token=False)
    
    # do we have a record_id?
    record_id = request.GET.get('record_id', None)
    carenet_id = request.GET.get('carenet_id', None)
    
    # prepare request token parameters
    params = {'oauth_callback':'oob'}
    if record_id:
        params['indivo_record_id'] = record_id
    if carenet_id:
        params['indivo_carenet_id'] = carenet_id
    
    # request a request token
    req_token = client.fetch_request_token(params)

    # store the request token in the session for when we return from auth
    request.session['request_token'] = req_token
    
    # redirect to the UI server
    return HttpResponseRedirect(client.auth_redirect_url)

def after_auth(request):
    """
    after Indivo authorization, exchange the request token for an access token and store it in the web session.
    """
    # get the token and verifier from the URL parameters
    oauth_token, oauth_verifier = request.GET['oauth_token'], request.GET['oauth_verifier']
    
    # retrieve request token stored in the session
    token_in_session = request.session['request_token']
    
    # is this the right token?
    if token_in_session['oauth_token'] != oauth_token:
        return HttpResponse("oh oh bad token")
    
    # get the indivo client and use the request token as the token for the exchange
    client = get_indivo_client(request, with_session_token=False)
    client.update_token(token_in_session)
    access_token = client.exchange_token(oauth_verifier)

    # store stuff in the session
    request.session['access_token'] = access_token
    
    if access_token.has_key('xoauth_indivo_record_id'):
        request.session['record_id'] = access_token['xoauth_indivo_record_id']
        if request.session.has_key('carenet_id'):
            del request.session['carenet_id']
    else:
        if request.session.has_key('record_id'):
            del request.session['record_id']
        request.session['carenet_id'] = access_token['xoauth_indivo_carenet_id']
    
    return index(request)

def index(request):
    return list_labs(request)

def parse_labs(labs):
    
    def _process_lab(lab):
        lab['id'] = lab['__documentid__']
        del lab['__documentid__']

        # Parse the lab's date
        try:
            d = dateutil.parser.parse(lab['collected_at'])
            d = d.astimezone(dateutil.tz.tzutc())
        except ValueError as e:
            d = 'parse error'
        lab['collected_at'] = d
        
        # Normalize the lab's status text
        if lab['status_identifier'] in LAB_STATUSES:
            lab['status_title'] = LAB_STATUSES[lab['status_identifier']]
        else:
            lab['status_title'] = 'Unknown'

        # Determine if the lab is abnormal
        try:
            # See if we can determine if value is outside the normal min/max
            test_value = float(lab['quantitative_result_value_value'])
            min = float(lab['quantitative_result_normal_range_min_value'])
            max = float(lab['quantitative_result_normal_range_max_value'])
            if test_value > max or test_value < min:
                lab['abnormal'] = True

            # labs are also abnormal if they are explicitly labeled as such
            abn_interp = lab.get('abnormal_interpretation_identifier', None)
            if abn_interp and abn_interp != 'normal':
                lab['abnormal'] = True
        except (KeyError, ValueError, TypeError) as e:
            pass

        # Preprocess the lab's address and organization names
        lab['org'] = lab['collected_by_org_name'] or 'Not Supplied'
        prefix = 'collected_by_org_adr_'
        adr_fields = (
            lab[prefix+'street'],
            lab[prefix+'city'],
            lab[prefix+'region'],
            lab[prefix+'postalcode'],
            lab[prefix+'country'],
            )
        lab['adr'] = ', '.join([f for f in adr_fields if f]) or 'Not Supplied'

        return lab
        
    return map(_process_lab, labs)

def show_lab(request, lab_id):
    client = get_indivo_client(request)
    record_id = request.session['record_id']
    resp, doc = client.record_specific_document(record_id=record_id, document_id=lab_id)
    if resp['status'] != '200':
        # TODO: handle errors
        raise Exception("Error loading original lab document: %s"%doc)
    lab = etree.fromstring(doc)
    return render_to_response("labs/templates/show.html", {'lab':etree.tostring(lab, pretty_print=True), 
                                                           'STATIC_HOME': settings.STATIC_HOME}
    )

def list_labs(request):
    # read in query params
    limit = int(request.GET.get('limit', 15))
    offset = int(request.GET.get('offset', 0))
    order_by = request.GET.get('order_by', 'collected_at') # test_name_title, created_at, collected_at
    lab_status = request.GET.get('lab_status', 'All') # final, corrected, preliminary
    lab_status_display = LAB_STATUSES.get(lab_status, 'All')

    #read in previous values from session
    previous_date_start = request.session.get("date_start", None)
    previous_date_end = request.session.get("date_end", None)

    if request.session.has_key('record_id'):
        record_id = request.session['record_id']
        client = get_indivo_client(request)

        # retrieve a min date for labs
        oldest_params = {'limit': '1', 'order_by': 'collected_at'}
        if lab_status in LAB_STATUSES:
            oldest_params['status_identifier'] = lab_status
        resp, content = client.generic_list(record_id=record_id, data_model="LabResult", body=oldest_params)
        if resp['status'] != '200':
            # TODO: handle errors
            raise Exception("Error fetching oldest lab: %s"%content)
        oldest_lab = parse_labs(simplejson.loads(content))
        if len(oldest_lab) > 0:
            oldest_lab_date = oldest_lab[0]['collected_at']
        else:
            oldest_lab_date = datetime.datetime.utcnow()

        max_date_string = datetime.datetime.utcnow().isoformat() + 'Z'
        min_date_string = datetime.datetime.combine(oldest_lab_date, datetime.time()).isoformat() + 'Z'
        date_start_string = request.GET.get('date_start', min_date_string)
        date_end_string = request.GET.get('date_end', max_date_string)
        
        #resets when changing date start/end
        if previous_date_start != date_start_string or previous_date_end != date_end_string:
            offset = 0
            
        #save off params in session
        request.session['date_start'] = date_start_string        
        request.session['date_end'] =  date_end_string
        
        # set params for lab query    
        parameters = {'limit': limit, 'offset': offset, 'order_by': order_by}
        parameters.update({'date_range': 'collected_at*' + date_start_string + '*' + date_end_string})
        if lab_status in LAB_STATUSES:
            parameters['status_identifier'] = lab_status
        resp, content = client.generic_list(record_id=record_id, data_model="LabResult", body=parameters)
        if resp['status'] != '200':
            # TODO: handle errors
            raise Exception("Error fetching labs: %s"%content)
        labs = parse_labs(simplejson.loads(content))
    else:
        #TODO: not the case anymore
        print 'FIXME: no client support for labs via carenet. See problems app for an example.. Exiting...'
        return
    
    # build a description for the range of results shown and calculate offsets
    next_offset = None
    prev_offset = None
    num_labs = len(labs)
    if num_labs == 0 and offset == 0:
        range_description = 'No Results'
    elif num_labs == 0:
        range_description = 'End of Results'
    else:
        range_description = 'Showing Results ' + str(offset + 1) + '-' + str(offset + num_labs)
        if limit == num_labs:
            next_offset = offset + limit
         
    if offset > 0:
        prev_offset = offset - limit
        if prev_offset < 0:
            prev_offset = 0
            
    return render_to_response("labs/templates/list.html", {'labs': labs, 
                                                           'lab_statuses': LAB_STATUSES,
                                                           'STATIC_HOME': settings.STATIC_HOME,
                                                           'order_by': order_by,
                                                           'limit': limit,
                                                           'offset': offset,
                                                           'lab_status_id': lab_status,
                                                           'lab_status_display': lab_status_display,
                                                           'next_offset': next_offset,
                                                           'prev_offset': prev_offset,
                                                           'range_description': range_description,
                                                           'num_labs': num_labs,
                                                           'min_date': min_date_string,
                                                           'max_date': max_date_string,
                                                           'date_start': date_start_string,
                                                           'date_end': date_end_string}
    )
    
