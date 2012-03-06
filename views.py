""" 

"""

from lxml import etree
from utils import *
from django.shortcuts import render_to_response
import settings # app local
import dateutil.parser

NS = 'http://indivo.org/vocab/xml/documents#'

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
    
    params['offline'] = 1
    
    # request a request token
    request_token = parse_token_from_response(client.post_request_token(data=params))
    
    # store the request token in the session for when we return from auth
    request.session['request_token'] = request_token
    
    # redirect to the UI server
    return HttpResponseRedirect(settings.INDIVO_UI_SERVER_BASE + '/oauth/authorize?oauth_token=%s' % request_token['oauth_token'])

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
    
    # create the client
    params = {'oauth_verifier' : oauth_verifier}
    access_token = parse_token_from_response(client.post_access_token(data=params))
    
    # store stuff in the session
    request.session['access_token'] = access_token
    
    if access_token.has_key('xoauth_indivo_record_id'):
        request.session['record_id'] = access_token['xoauth_indivo_record_id']
    else:
        if request.session.has_key('record_id'):
            del request.session['record_id']
        request.session['carenet_id'] = access_token['xoauth_indivo_carenet_id']
    
    # now get the long-lived token using this access token
    client= get_indivo_client(request)
    try:
        long_lived_token = parse_token_from_response(client.get_long_lived_token())
        
        request.session['long_lived_token'] = long_lived_token
    except:
        pass
    return index(request)

def index(request):
    return list_labs(request)

def get_labs(root):
    labs = []
    reportNodes = root.findall('.//Report')
        
    for r in reportNodes:
        d = r.findtext('.//{%s}dateMeasured' % NS, default='')
        try:
            # parse date string and set timezone as UTC
            d = dateutil.parser.parse(d)
            d = d.astimezone(dateutil.tz.tzutc())
        except ValueError as e:
            d = 'parse error'
            
        lab = {
                 'dateMeasured': d,
                 'labType': r.findtext('.//{%s}labType' % NS, default=''),
                 'laboratory': {
                        'name': r.findtext('.//{%s}name' % NS, default=''),
                        'address': r.findtext('.//{%s}address' % NS, default='')
                         },
                 'comments': r.findtext('.//{%s}comments' % NS, default=''),
                 'firstLabTestName': r.findtext('.//{%s}firstLabTestName' % NS, default=''),
                 'firstLabTestValue': r.findtext('.//{%s}firstLabTestValue' % NS, default=''),
                 'normalRangeMinimum': r.findtext('.//{%s}normalRangeMinimum' % NS, default=''),
                 'normalRangeMaximum': r.findtext('.//{%s}normalRangeMaximum' % NS, default=''),
                 # meta information
                 'id': r.find('.//Document').attrib['id']
        }
        
        try:
            # See if we can determine if value is outside the normal min/max
            test_value = float(lab.firstLabTestValue)
            min = float(lab.normalRangeMinimum)
            max = float(lab.normalRangeMaximum)
            if test_value > max or test_value < min:
                lab.update({'abnormal': True})
        except Exception as e:
            pass
        
        labs.append(lab)
        
    return labs

def show_lab(request, lab_id):
    client = get_indivo_client(request)
    record_id = request.session['record_id']
    doc = client.read_document(record_id=record_id, document_id=lab_id)
    lab = etree.fromstring(doc.response['response_data'])
    return render_to_response("labs/templates/show.html", {'lab':etree.tostring(lab, pretty_print=True), 
                                                           'STATIC_HOME': settings.STATIC_HOME}
    )

def list_labs(request):
    # read in query params
    limit = int(request.GET.get('limit', 15))
    offset = int(request.GET.get('offset', 0))
    order_by = request.GET.get('order_by', 'date_measured') # lab_test_name, lab_type, created_at, date_measured
    lab_type = request.GET.get('lab_type', 'All')
    
    
    #read in previous values from session
    previous_date_start = request.session.get("date_start", None)
    previous_date_end = request.session.get("date_end", None)

    if request.session.has_key('record_id'):
        record_id = request.session['record_id']
        # retrieve list of lab_types for this record
        lab_types = []
        client = get_indivo_client(request)
        lab_type_list = client.read_labs(record_id = record_id, parameters = {'group_by': 'lab_type', 'aggregate_by': 'count*lab_type'}).response['response_data']
        lab_type_root = etree.XML(lab_type_list)
        for aggregateReport in lab_type_root.findall('.//{%s}AggregateReport' % NS):
            lab_types.append(aggregateReport.attrib['group'])
        lab_types.sort()
        # retrieve a min date for labs
        oldest_params = {'limit': '1', 'order_by': 'date_measured'}
        if lab_type in lab_types:
            oldest_params.update({'lab_type': lab_type})
        oldest_lab = get_labs(etree.XML(client.read_labs(record_id = record_id, parameters = oldest_params).response['response_data']))
        if len(oldest_lab) > 0:
            oldest_lab_date = oldest_lab[0]['dateMeasured']
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
        if lab_type in lab_types:
            parameters.update({'lab_type': lab_type})
        parameters.update({'date_range': 'date_measured*' + date_start_string + '*' + date_end_string})
        labs_xml = client.read_labs(record_id = record_id, parameters = parameters).response['response_data']
        #TODO: check response status
    else:
        #TODO: not the case anymore
        print 'FIXME: no client support for labs via carenet. See problems app for an example.. Exiting...'
        return
    
    # parse labs
    labs_root = etree.XML(labs_xml)
    labs = get_labs(labs_root)
    
    # build a description for the range of results shown and calculate offsets
    next_offset = None
    prev_offset = None
    total_document_count = int(labs_root.find('.//Summary').attrib['total_document_count'])
    if total_document_count <= 0:
        range_description = 'No Results'
    elif offset + limit < total_document_count:
        next_offset = offset + limit
        range_description = 'Showing ' + str(offset + 1) + '-' + str(offset + limit) + ' of ' +  str(total_document_count)
    else:
         range_description = 'Showing ' + str(offset + 1) + '-' + str(total_document_count) + ' of ' +  str(total_document_count)
         
    if offset > 0:
        prev_offset = offset - limit
        if prev_offset < 0:
            prev_offset = 0
            
    return render_to_response("labs/templates/list.html", {'labs': labs, 
                                                           'lab_types': lab_types,
                                                           'STATIC_HOME': settings.STATIC_HOME,
                                                           'order_by': order_by,
                                                           'limit': limit,
                                                           'offset': offset,
                                                           'lab_type': lab_type,
                                                           'next_offset': next_offset,
                                                           'prev_offset': prev_offset,
                                                           'range_description': range_description,
                                                           'total_document_count': total_document_count,
                                                           'min_date': min_date_string,
                                                           'max_date': max_date_string,
                                                           'date_start': date_start_string,
                                                           'date_end': date_end_string}
    )
    