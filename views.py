""" 
Arjun Sanyal arjun.sanyal@childrens.harvard.edu

TODO: use lxml here. which is a lot more pythonic. See http://codespeak.net/lxml/tutorial.html

"""

DEBUG = True

from pprint import pprint as pp
from utils import *
from django.utils import simplejson
from xml.etree import ElementTree
from django.shortcuts import render_to_response
import settings # app local

NS = '{http://indivo.org/vocab/xml/documents#}'
XSI = '{http://www.w3.org/2001/XMLSchema-instance}'

lab_types_categories_list = [
  'Hematology',
  'Chemistry',
  'Urinalysis',
  'Endocrinology',
  'Microbiology',
  'Uncategorized'
]

# order is "lowest first"
lab_names_to_categories_map = {
  '(PTH) Parathyroid Hormone Level'                    : {'category': 'Endocrinology',  'order': None}
 ,'ABO RH TYPE'                                        : {'category': 'Hematology',     'order': None}
 ,'ALT'                                                : {'category': 'Chemistry',      'order': None}
 ,'ANTIBODY SCREEN PHASES & INTRP'                     : {'category': 'Hematology',     'order': None}
 ,'AST (Aspartate Aminotransferase)'                   : {'category': 'Chemistry',      'order': None}
 ,'Albumin'                                            : {'category': 'Chemistry',      'order': None}
 ,'Alkaline Phosphatase'                               : {'category': 'Chemistry',      'order': None}
 ,'Ammonia (NH3)'                                      : {'category': 'Chemistry',      'order': None}
 ,'Amylase Level'                                      : {'category': 'Chemistry',      'order': None}
 ,'Anaerobic Culture'                                  : {'category': 'Microbiology',   'order': None}
 ,'BUN'                                                : {'category': 'Chemistry',      'order': None}
 ,'Bilirubin, Total + Direct, Plasma'                  : {'category': 'Chemistry',      'order': None}
 ,'Blood Culture, Aerobic and Anaerobic'               : {'category': 'Microbiology',   'order': None}
 ,'C. difficile Toxin'                                 : {'category': 'Microbiology',   'order': None}
 ,'CMV PCR'                                            : {'category': 'Microbiology',   'order': None}
 ,'CO2'                                                : {'category': 'Chemistry',      'order': None}
 ,'Calcium'                                            : {'category': 'Chemistry',      'order': None}
 ,'Calcium Ionized'                                    : {'category': 'Chemistry',      'order': None}
 ,'Chemistry Extended Panel (Chem 7 PLUS Ca,Mg,Phos)'  : {'category': 'Chemistry',      'order': None}
 ,'Chemistry Panel (Na,K,Cl,CO2,BUN,Cr,Glu)'           : {'category': 'Chemistry',      'order': None}
 ,'Cholesterol'                                        : {'category': 'Chemistry',      'order': None}
 ,'Complete Blood Count'                               : {'category': 'Hematology',     'order': 3}
 ,'Complete Blood Count with Differential'             : {'category': 'Hematology',     'order': 2}
 ,'CreatININE, Urine'                                  : {'category': 'Urinalysis',     'order': None}
 ,'Creatinine'                                         : {'category': 'Chemistry',      'order': None}
 ,'Cytomegalovirus, IgG'                               : {'category': 'Microbiology',   'order': None}
 ,'Cytomegalovirus, IgM'                               : {'category': 'Microbiology',   'order': None}
 ,'Differential, manual'                               : {'category': 'Hematology',     'order': None}
 ,'EBV Antibody IgM'                                   : {'category': 'Microbiology',   'order': None}
 ,'EBV Antibody to EA-D, IgG'                          : {'category': 'Microbiology',   'order': None}
 ,'EBV Antibody to NA, IgG'                            : {'category': 'Microbiology',   'order': None}
 ,'EBV Capsid Antigen, IgG'                            : {'category': 'Microbiology',   'order': None}
 ,'Electrolytes'                                       : {'category': 'Chemistry',      'order': None}
 ,'Electrolytes, Urine'                                : {'category': 'Urinalysis',     'order': None}
 ,'Ferritin'                                           : {'category': 'Hematology',     'order': None}
 ,'Fibrinogen'                                         : {'category': 'Hematology',     'order': None}
 ,'Fungus Culture'                                     : {'category': 'Microbiology',   'order': None}
 ,'Glucose Level'                                      : {'category': 'Chemistry',      'order': None}
 ,'HDLC'                                               : {'category': 'Chemistry',      'order': None}
 ,'Hematocrit'                                         : {'category': 'Hematology',     'order': 4}
 ,'Hemoglobin'                                         : {'category': 'Hematology',     'order': 5}
 ,'Hepatitis A IgM'                                    : {'category': 'Microbiology',   'order': None}
 ,'Hepatitis A Panel (Total + IgM)'                    : {'category': 'Microbiology',   'order': None}
 ,'Iron Binding Capacity, Total'                       : {'category': 'Hematology',     'order': None}
 ,'Iron, Plasma'                                       : {'category': 'Hematology',     'order': None}
 ,'LDH (Lactate Dehydrogenase)'                        : {'category': 'Chemistry',      'order': None}
 ,'Lipase Level'                                       : {'category': 'Chemistry',      'order': None}
 ,'Lipid Profile, Fasting'                             : {'category': 'Chemistry',      'order': None}
 ,'Liver Function Tests plus GGT'                      : {'category': 'Chemistry',      'order': None}
 ,'MRSA Culture'                                       : {'category': 'Microbiology',   'order': None}
 ,'Magnesium'                                          : {'category': 'Chemistry',      'order': None}
 ,'Manual Interpretation Oximetry'                     : {'category': 'Hematology',     'order': None}
 ,'Measles(Rubeola), IgG'                              : {'category': 'Microbiology',   'order': None}
 ,'Mumps, IgG'                                         : {'category': 'Microbiology',   'order': None}
 ,'Neurontin'                                          : {'category': 'Chemistry',      'order': None}
 ,'OR VBG Profile'                                     : {'category': 'Uncategorized',  'order': None}
 ,'Osmolality'                                         : {'category': 'Chemistry',      'order': None}
 ,'Oximetry'                                           : {'category': 'Uncategorized',  'order': None}
 ,'PTT (Partial Thromboplastin)'                       : {'category': 'Hematology',     'order': None}
 ,'Patient Data PFT'                                   : {'category': 'Uncategorized',  'order': None}
 ,'Phosphorus'                                         : {'category': 'Chemistry',      'order': None}
 ,'Polyomavirus BK PCR'                                : {'category': 'Microbiology',   'order': None}
 ,'Potassium Level'                                    : {'category': 'Chemistry',      'order': None}
 ,'Protein Random, Urine'                              : {'category': 'Urinalysis',     'order': None}
 ,'Prothrombin Time (includes INR)'                    : {'category': 'Hematology',     'order': None}
 ,'Reticulocyte Count'                                 : {'category': 'Hematology',     'order': None}
 ,'Rubella IgG'                                        : {'category': 'Microbiology',   'order': None}
 ,'Smear For RBC Morphology Only'                      : {'category': 'Hematology',     'order': None}
 ,'Source CMV'                                         : {'category': 'Microbiology',   'order': None}
 ,'Source, Stone Analysis'                             : {'category': 'Chemistry',      'order': None}
 ,'Stone Analysis'                                     : {'category': 'Chemistry',      'order': None}
 ,'Tacrolimus Level'                                   : {'category': 'Chemistry',      'order': None}
 ,'Thrombin Time'                                      : {'category': 'Hematology',     'order': None}
 ,'Total Protein'                                      : {'category': 'Chemistry',      'order': None}
 ,'Toxoplasma, IgG'                                    : {'category': 'Microbiology',   'order': None}
 ,'Toxoplasma, IgM'                                    : {'category': 'Microbiology',   'order': None}
 ,'Transferrin'                                        : {'category': 'Chemistry',      'order': None}
 ,'Triglycerides'                                      : {'category': 'Chemistry',      'order': None}
 ,'Uric Acid'                                          : {'category': 'Chemistry',      'order': None}
 ,'Urinalysis, Macroscopic'                            : {'category': 'Urinalysis',     'order': None}
 ,'Urine Culture'                                      : {'category': 'Microbiology',   'order': None}
 ,'VRE Culture, Rectal'                                : {'category': 'Microbiology',   'order': None}
 ,'Vancomycin Level, Random'                           : {'category': 'Chemistry',      'order': None}
 ,'Vancomycin Level, Trough (Pre)'                     : {'category': 'Chemistry',      'order': None}
 ,'Varicella zoster Anitbody, IgG'                     : {'category': 'Microbiology',   'order': None}
 ,'Varicella-Zoster Antibody, IgM'                     : {'category': 'Microbiology',   'order': None}
 ,'WBC Differential, Automated'                        : {'category': 'Hematology',     'order': 1}
 ,'Wound Culture and Gram Stain'                       : {'category': 'Microbiology',   'order': None}
 ,'microbiology'                                       : {'category': 'Microbiology',   'order': None}
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
    """pass the record_id to JMVC and use the JSON/REST api from there"""

    return render_to_response(
        # settings.JMVC_HOME+'labs/'+settings.SUBMODULE_NAME+'.html',
        settings.JS_HOME+'/'+settings.SUBMODULE_NAME+'.html',
        {'SUBMODULE_NAME': settings.SUBMODULE_NAME,
         'INDIVO_UI_APP_CSS': settings.INDIVO_UI_SERVER_BASE+'/jmvc/ui/resources/css/ui.css'}
    )

def list_labs(request):
    limit = int(request.GET.get('limit', 100)) # defaults
    offset = int(request.GET.get('offset', 0))
    client = get_indivo_client(request)
    
    if request.session.has_key('record_id'):
        record_id = request.session['record_id']
        record = parse_xml(client.read_record(record_id = record_id).response['response_data'])
        parameters = {'limit': limit, 'offset': offset, 'order_by': 'date_measured'}
        labs_xml = client.read_labs(record_id = record_id, parameters = parameters).response['response_data']
    else:
        print 'FIXME: no client support for labs via carenet. See problems app for an example.. Exiting...'
        return
        
    reports_et_list = list(parse_xml(labs_xml))
    reports = {
      'lab_types_categories_list': lab_types_categories_list,
      'lab_names_to_categories_map': lab_names_to_categories_map,
      'summary': {
        'total_document_count': reports_et_list[0].attrib['total_document_count'],
        'limit':                reports_et_list[0].attrib['limit'],
        'offset':               reports_et_list[0].attrib['offset'],
        'order_by':             reports_et_list[0].attrib['order_by'],
        'total_pages_count':    int(reports_et_list[0].attrib['total_document_count']) / limit,
        'current_page':         (offset / limit) + 1    # 1-index this
      },
      'reports': []
    }
    
    def _parse_report(report):
      meta = report.find('Meta')
      item = report.find('Item')
      document = meta.find('Document')
      doc_xml = client.read_document(record_id = record_id, document_id = document.attrib['id']).response['response_data']
      
      # if DEBUG: print '\n'+doc_xml
      
      lab = parse_xml(doc_xml)
      
      # FIXME: get metadata
      # FIXME: get metadata
      # FIXME: get metadata
      
      # todo: if this is a microbiology tab, punt
      # todo: if this is a microbiology tab, punt
      # todo: if this is a microbiology tab, punt

      if lab.find(NS+'labType').text == 'Bacteriology':
        return False
        
      laboratory = lab.find(NS+'laboratory')
      if laboratory and laboratory.find(NS+'name').text == 'Bacteriology':
        return False
        
      return {
        'meta':  meta.text,
        'item': _parse_lab(lab)
      }
    
    def _parse_lab(lab):
      """ Each lab can have 0 to n panels (including 0 to n tests) and 0 to n 'standalone' tests """
      panels = []
      tests = []
      laboratory = lab.find(NS+'laboratory')
      
      # get panels
      for panel in [c for c in lab.getchildren() if c.tag.find(NS+'labPanel') >= 0]:
        panels.append(_parse_panel(panel))
        
      # get "standalone" tests
      for test in [c for c in lab.getchildren() if c.tag.find(NS+'labTest') >= 0]:
        tests.append(_parse_test(test))
        
      # see indivo_server/schemas/lab.xsd
      if lab.find(NS+'comments'):
        comments = lab.find(NS+'comments').text
      else:
        comments = ''
        
      lab_name_for_categorization = ''
      if len(tests):
        lab_name_for_categorization = tests[0]['name_value']
      else:
        lab_name_for_categorization = panels[0]['name']
      
      c = lab_names_to_categories_map.get(lab_name_for_categorization, {'category': 'Uncategorized', 'order': None})
      
      # print '---> name: '+lab_name_for_categorization
      # print '--->  cat: '+c['category']
      # print '\n'
      
      out = {
        'date_measured' : lab.find(NS+'dateMeasured').text    if lab.find(NS+'dateMeasured').tag.find('dateMeasured') else '',
        'type'          : lab.find(NS+'labType').text         if lab.find(NS+'labType').tag.find('labType') else '',
        'lab_name'      : laboratory.find(NS+'name').text     if laboratory and laboratory.find(NS+'name').tag.find('name') else '', 
        'lab_address'   : laboratory.find(NS+'address').text  if laboratory and laboratory.find(NS+'address').tag.find('address') else '',
        'panels'        : panels,
        'tests'         : tests,
        'comments'      : comments,
        'category'      : c['category'],
        'order'         : c['order'],
        'lab_name_for_categorization': lab_name_for_categorization
      }

      return out
    
    def _parse_panel(p):
        panel = {
            'name': p[0].get('value', ''),
            'tests': []
        }
        
        test_idx = 1
        while test_idx < len(p) and p[test_idx].tag.find('labTest') > 0:
            test = _parse_test(p[test_idx])
            panel['tests'].append(test)
            test_idx = test_idx + 1
        
        return panel
    
    def _parse_test(t):
        test = {
            'date_measured'     : t[0].text             if t[0].tag.find('dateMeasured') else '',
            'name_abbreviation' : t[1].get('abbrev')    if t[1].tag.find('name') else '',
            'name_value'        : t[1].text             if t[1].tag.find('name') else '',
            'final'             : t[2].text             if t[2].tag.find('final') else '',
            'results'           : []
        }
        
        # NOTE: we might need to work around some malformed data with a missing result
        if len(t) != 4:
          print '\n\n\n\n---------------------------- bad data, no result! \n\n\n'
          raise "bad data, no result!"
          
        # FIXME: this is different than the lab.xml sample file in the indivo server document schemas
        # <labTest xsi:type="SingleResultLabTest">
        
        # if t.get('class').find('SingleResultLabTest'):
        if t.get(XSI+'type') == 'SingleResultLabTest':
            test['results'] = _parse_single_result(t[3])
        else:
            raise 'Multiple Result lab tests not implimented!'
        
        return test
    
    def _parse_single_result(r):
        result = {}
        flag_p = 0
        
        # zero or one flag
        if r[0].tag.find('flag') > 0:
            result['flag_abbreviation'] = r[0].get('abbrev','')
            result['flag_value'] = r[0].get('value', '')
            # if there's no flag, pass the whole set, otherwise slice it off
            flag_p = 1
            
        # if r.get('class').find('ResultInRange') > 0:
        if r.get(XSI+'type') == 'ResultInRange':
            result.update(_parse_result_in_range(r[flag_p:len(r)]))
        elif r.get('class').find('ResultInSet') > 0:
            result.update(_parse_result_in_set(r[flag_p:len(r)]))
        else:
            raise 'Bad result type'

        return result
    
    def _parse_result_in_range(v):
        if not v[0].tag == NS+'valueAndUnit':
            raise 'valueAndUnit tag expected but not found!'
            
        # a sequence of:
        # 1 valueAndUnit (** required)
        #   0 or 1 value
        #   0 or 1 textValue
        #   0 or 1 unit
        # 0 or 1 normalRange
        #   0 or 1 minimum
        #   0 or 1 maximum
        #   0 or 1 unit
        # 0 or 1 nonCriticalRange
        
        # FIXME: we really need an iterator here or some better way to do this
        # FIXME: we really need an iterator here or some better way to do this
        # FIXME: we really need an iterator here or some better way to do this
        
        # FIXME: value_textvalue
        # FIXME: value_textvalue
        # FIXME: value_textvalue

        # valueAndUnit might be an empty node
        if len(v[0]) == 0: return {}
        
        # result = {
        #   'value'                                 : v[0][0].text          if v[0][0].tag.find('value') else '',
        #   #  'value_textvalue':              : v[0][1].text if v[0][1].tag.find('textValue')
        #   # TODO: unit here is really a "coded value", which should be parsed on its own
        # }
        
        # # textValue and unit are optional
        # if len(v[0]) > 1:
        #   result.update({
        #     'value_unit'                            : v[0][1].get('value')  if v[0][1].tag.find('unit') else '',
        #     'value_abbreviation'                    : v[0][1].get('abbrev') if v[0][1].tag.find('unit') else '',
        #   })
        # 
        # import pdb; pdb.set_trace()
        # 
        # if len(v) > 1 and v[1].tag.find("normalRange") and len(v[1].getchildren()) > 0:
        #   result.update({
        #     'normal_range_minimum'                  : v[1][0].text          if v[1][0].tag.find('minimum') else '',
        #     'normal_range_maximum'                  : v[1][1].text          if v[1][1].tag.find('maximum') else '',
        #   })
        #   if len(v[1]) > 2:
        #     result.update({
        #     'normal_range_unit'                     : v[1][2].get('value')  if v[1][2].tag.find('unit') else '',
        #     'normal_range_unit_abbreviation'        : v[1][2].get('abbrev') if v[1][2].tag.find('unit') else '',
        #     })
        #     
        # if len(v) > 2 and v[1].tag.find("nonCriticalRange"):
        #   result.update({
        #     'non_critical_range_minimum'            : v[2][0].text          if v[2][0].tag.find('minimum') else '',
        #     'non_critical_range_maximum'            : v[2][1].text          if v[2][1].tag.find('maximum') else '',
        #     'non_critical_range_unit'               : v[2][2].get('value')  if v[2][2].tag.find('unit') else '',
        #     'non_critical_range_unit_abbreviation'  : v[2][2].get('abbrev') if v[2][2].tag.find('unit') else ''
        #   })

        result = {}
        
        for e in v:
          if e.tag == NS+'valueAndUnit':
            result.update({
              'value'                                   : e[0].text             if e[0].tag.find('value') else ''
            })

            if len(e) > 1:
              result.update({
                'value_unit'                            : e[1].get('value')  if e[1].tag.find('unit') else '',
                'value_abbreviation'                    : e[1].get('abbrev') if e[1].tag.find('unit') else '',
              })
            
          elif len(e) > 0 and e.tag == NS+'normalRange':
            import pdb; pdb.set_trace()            
            result.update({
              'normal_range_minimum'                  : v[1][0].text          if v[1][0].tag.find('minimum') else '',
              'normal_range_maximum'                  : v[1][1].text          if v[1][1].tag.find('maximum') else '',
            })
          
            #   if len(v[1]) > 2:
            #     result.update({
            #     'normal_range_unit'                     : v[1][2].get('value')  if v[1][2].tag.find('unit') else '',
            #     'normal_range_unit_abbreviation'        : v[1][2].get('abbrev') if v[1][2].tag.find('unit') else '',
            #     })
          
          elif len(e) > 0 and e.tag == NS+'nonCriticalRange':
            import pdb; pdb.set_trace()
            result.update({
              'non_critical_range_minimum'            : v[2][0].text          if v[2][0].tag.find('minimum') else '',
              'non_critical_range_maximum'            : v[2][1].text          if v[2][1].tag.find('maximum') else '',
              'non_critical_range_unit'               : v[2][2].get('value')  if v[2][2].tag.find('unit') else '',
              'non_critical_range_unit_abbreviation'  : v[2][2].get('abbrev') if v[2][2].tag.find('unit') else ''
            })

        return result
    
    def _parse_result_in_set(v):
        if not v[0].tag == NS+'value':
            raise 'value tag expected but not found!'
        
        value = v[0].text
        options = []
        
        i = 1
        while i < len(v):
            options.append({
                'normal': v[i].get('normal'),
                'description': v[i].get('description', ''),
                'value': v[i].text
            })
            i = i + 1
            
        return {
            'value': value,
            'options': options
        }
    
    
    #
    # code for new "latest of each lab type" display
    #
    # note: we depend on the reports being ordered by date_measured
    # it's ascending by default, hence the reverse()
    seen_lab_types_count = {}
    reports_for_parsing = reports_et_list[1:]
    reports_for_parsing.reverse()
    reports['latest_reports'] = []
    
    for r in reports_for_parsing:
      item = r.find('Item')
      lab = item.find(NS+'LabReport')
      lab_type = lab.find(NS+'labType').text
      
      parsed_report = _parse_report(r)
      
      if parsed_report:
        reports['reports'].append(parsed_report)
      else:
        continue
      
      name_for_cat =  parsed_report['item']['lab_name_for_categorization']
      if not name_for_cat in seen_lab_types_count:
        seen_lab_types_count[name_for_cat] = 1
        reports['latest_reports'].append(parsed_report)
      else:
        if seen_lab_types_count[name_for_cat] == 1:
          reports['latest_reports'].append(parsed_report)
          seen_lab_types_count[name_for_cat] = 2
        else:
          continue
          
    if DEBUG:
      # print simplejson.dumps(reports)
      pass
      
    return HttpResponse(simplejson.dumps(reports), mimetype='text/plain')

def new_lab():
    """docstring for new_lab"""
    # def new_problem(request):
    #     if request.method == "GET":
    #         return render_template('newproblem')
    #     else:
    #         # get the variables and create a problem XML
    #         params = {'code_abbrev':'', 'coding_system': 'umls-snolab', 'date_onset': request.POST['date_onset'], 'date_resolution': request.POST['date_resolution'], 'code_fullname': request.POST['code_fullname'], 'code': request.POST['code'], 'diagnosed_by' : request.POST['diagnosed_by'], 'comments' : request.POST['comments']}
    #         problem_xml = render_raw('problem', params, type='xml')
    #         
    #         # add the problem
    #         client = get_indivo_client(request)
    #         client.post_document(record_id = request.session['record_id'], data=problem_xml)
    #         
    #         # add a notification
    #         client.record_notify(record_id = request.session['record_id'], data={'content':'a new problem has been added to your problem list'})
    #         
    #         return HttpResponseRedirect(reverse(problem_list))
    pass

def one_lab():
    """docstring for one_lab"""
    # def one_problem(request, problem_id):
    #     client = get_indivo_client(request)
    #     
    #     record_id = request.session.get('record_id', None)
    #     
    #     if record_id:
    #         
    #         # get record information
    #         record = parse_xml(client.read_record(record_id = record_id).response['response_data'])
    #         
    #         doc_xml = client.read_document(record_id= record_id, document_id = problem_id).response['response_data']
    #         doc_meta_xml = client.read_document_meta(record_id=record_id, document_id= problem_id).response['response_data']
    #     else:
    #         carenet_id = request.session['carenet_id']
    #         
    #         record = parse_xml(client.get_carenet_record(carenet_id = carenet_id).response['response_data'])
    #         
    #         doc_xml = client.get_carenet_document(carenet_id= carenet_id, document_id = problem_id).response['response_data']
    #         #doc_meta_xml = client.get_carenet_document_meta(carenet_id=carenet_id, document_id= problem_id).response['response_data']
    #         doc_meta_xml = None
    #     
    #     doc = parse_xml(doc_xml)
    #     
    #     problem = parse_problem(doc)
    #     
    #     if doc_meta_xml:
    #         doc_meta = parse_xml(doc_meta_xml)
    #         meta = parse_meta(doc_meta)
    #     else:
    #         meta = None
    #     
    #     record_label = record.attrib['label']
    #     
    #     surl_credentials = client.get_surl_credentials()
    #     
    #     return render_template('one', {'problem':problem, 'record_label': record_label, 'meta': meta, 'record_id': record_id, 'problem_id': problem_id, 'surl_credentials': surl_credentials})
    pass
