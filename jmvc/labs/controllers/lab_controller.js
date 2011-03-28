/**
 * @tag controllers, home
 * @author Arjun Sanyal (arjun.sanyal@childrens.harvard.edu)
 * Displays a table of labs. No editing for now
 */
$.Controller.extend('Labs.Controllers.Lab',
/* @Static */
{ 
  onDocument: true,
  limit: 25,
  // offset: 0,
  details_p: false
},
/* @Prototype */
{
  _loading: function(n){
    n = n || '';
    if (n) { n = ' ' + n + ' labs'; }
    $('#loading').html('<h3>Loading' + n + '...</h3>').show();
  },

  ready: function(){
    if(!$("#lab").length) $(document.body).append($('<div/>').attr('id','lab'))
    $('#lab').html(this.view('loading'));
  },

  load: function(){
    var params = {
      // 'limit': Labs.Controllers.Lab.limit,
      // 'offset': Labs.Controllers.Lab.offset
    }
    Labs.Models.Lab.findAll(params, this.callback('list'));
  },

  list: function(labs){
    // we can use a callback here if we need strict ordering (e.g. for iframe resize)
    var _this = this;
    var callback = function() {
      $('#loading').hide();
      // categories to start hidden
      $('.category_toggle a').each(function(){$(this).click()})
    };
    var _show = function(callback) {
      // console.log(labs);

      $('#lab').html(_this.view('init',
        {'reports':labs.reports,
         'latest_reports': labs.latest_reports,
         'summary':labs.summary,
         'lab_types_categories_list': labs.lab_types_categories_list,
         'lab_types_to_categories_map': labs.lab_types_to_categories_map
        }));
      if(callback) { callback() }
    };
    _show(callback);
  },

  // _resize: function(){
  //   var h = $('#lab').height();
  //   $('html').height(h);
  //   $('body').height(h);
  // },

  "select#page_selector change": function(el){
    var offset = Labs.Controllers.Lab.limit * (el.val() - 1); // pages are 1-indexed
    Labs.Controllers.Lab.offset = offset;

    this._loading(Labs.Controllers.Lab.limit)

    var params = {
      'limit': Labs.Controllers.Lab.limit,
      'offset': offset
    }
    
    Labs.Models.Lab.findAll(params, this.callback('list'));
  },

  "select#limit_selector change": function(el){
    var limit = el.val();
    Labs.Controllers.Lab.limit = limit; // save in controller

    this._loading(limit);

    var params = {
      'limit': limit,
      'offset': Labs.Controllers.Lab.offset
    }
    
    Labs.Models.Lab.findAll(params, this.callback('list'));
  },
  
  ".test_inner a click": function(el){
    var href = el.attr('href').substring(1);
    $('#details_'+href).toggle(); // need to prepend here so we don't actually go to this anchor and move the page
  },
  
  "#toggle_all_details click": function(){
    Labs.Controllers.Lab.details_p = !!Labs.Controllers.Lab.details_p;
    if (Labs.Controllers.Lab.details_p) {
      $('#toggle_all_details').text('hide details')
    }
    $('.test_inner_details').toggle();
  },

  ".category_toggle a click": function(el){
    var e = $(el[0]);
    if (e.text() === 'hide') { e.text('show'); }
    else { e.text('hide'); }
    var href = e.attr('href').substring(1);
    $('#'+href+'_div').toggle();
  }
});