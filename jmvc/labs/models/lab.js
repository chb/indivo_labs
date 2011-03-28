/**
 * @tag models, home
 * Wraps backend lab services. No CUD for now
 */
$.Model.extend('Labs.Models.Lab',
/* @Static */
{
  /**
   * Retrieves labs data from your backend services. Sorts labs by dateMeasured desc by default. Can't use
   * parameters to the api call to do this if using test data since all data have the same created_at in the db
   */
  findAll : function(params, success, error){
    $.ajax({
      url: '/apps/labs/lab', // I'd prefer /labs (which I think is more semantic) but that's what they use
      type: 'get',
      dataType: 'json',
      data: params,
      success: this.callback(function(data, textStatus, xhr){
        // sort data by <Report><Item><dateMeasured>
        // data.reports = _(data.reports).sortBy(function(r){ return(r.item.date_measured); }).reverse();
        success(data);
      }),
      error: error,
      fixture: "//labs/fixtures/labs.json.get" //calculates the fixture path from the url and type.
    })
  }
},
/* @Prototype */
{})