// When any key is pressed on an editable field, this will be triggered.

// This catches the carat (^) in the filter box and does what is needed, beginning of line
$.tablesorter.filter.types.start = function( config, data ) {
        if ( /^\^/.test( data.iFilter ) ) {
                return data.iExact.indexOf( data.iFilter.substring(1) ) === 0;
        }
        return null;
};

// This catches the dollar sign ($) in the filter box and does what is needed, end of line
$.tablesorter.filter.types.end = function( config, data ) {
        if ( /\$$/.test( data.iFilter ) ) {
                var filter = data.iFilter,
                        filterLength = filter.length - 1,
                        removedSymbol = filter.substring(0, filterLength),
                        exactLength = data.iExact.length;
                return data.iExact.lastIndexOf(removedSymbol) + filterLength === exactLength;
        }
        return null;
};

// This is the tablesorter configuration with widgets.
$(function() {
  $(".custom-popup")
    .tablesorter({debug: true,
      theme: 'blue',
      widgets: ['saveSort', 'zebra', 'filter', 'stickyHeaders', 'columnSelector', 'editable'],
      widgetOptions: {
        filter_reset: '.reset',
        filter_saveFilters : true,
        saveSort: true,
        columnSelector_container : $('#columnSelector'),
        columnSelector_columns : {
          0 : "disable" /* disable; i.e. remove column from selector */
	        //1 : false,     /* start with column hidden */
	        //2 : false,      /* start with column visible; default for undefined columns */
	        //3 : false,
	        //4 : false
        }, 
        columnSelector_saveColumns: true,
        columnSelector_layout : '<label><input type="checkbox">{name}</label>',
        columnSelector_name  : 'data-selector-name',
        columnSelector_mediaquery: false,
        columnSelector_mediaqueryName: 'Auto: ',
        columnSelector_mediaqueryHidden: true,
        columnSelector_mediaqueryState: true,
        columnSelector_breakpoints : [ '20em', '30em', '40em', '50em', '60em', '70em' ],
        columnSelector_priority : 'data-priority',
        editable_columns       : [2,3,4,5,6],       // or "0-2" (v2.14.2); point to the columns to make editable (zero-based index)
        editable_enterToAccept : true,          // press enter to accept content, or click outside if false
        editable_autoAccept    : false,          // accepts any changes made to the table cell automatically (v2.17.6)
        editable_autoResort    : false,         // auto resort after the content has changed.
        editable_validate      : null,          // return a valid string: function(text, original, columnIndex) { return text; }
        editable_focused       : function(txt, columnIndex, $element) {
          // $element is the div, not the td
          // to get the td, use $element.closest('td')
          $element.addClass('focused');
        },
        editable_blur          : function(txt, columnIndex, $element) {
          // $element is the div, not the td
          // to get the td, use $element.closest('td')
          $element.removeClass('focused');
        },
        editable_selectAll     : function(txt, columnIndex, $element) {
          // note $element is the div inside of the table cell, so use $element.closest('td') to get the cell
          // only select everthing within the element when the content starts with the letter "B"
          return /^b/i.test(txt) && columnIndex === 0;
        },
        editable_wrapContent   : '<div>',       // wrap all editable cell content... makes this widget work in IE, and with autocomplete
        editable_trimContent   : true,          // trim content ( removes outer tabs & carriage returns )
        editable_noEdit        : 'no-edit',     // class name of cell that is not editable
        editable_editComplete  : 'editComplete' // event fired after the table content has been edited
      }
    })
    // config event variable new in v2.17.6
    .children('tbody').on('editComplete', 'td', function(event, config) {
      var $this = $(this),
        newContent = $this.text(),
        cellIndex = this.cellIndex, // there shouldn't be any colspans in the tbody
        rowIndex = this.id; // data-row-index stored in row id
        rowHost = this.dataset.name; // data-row-index stored in row id

      // Do whatever you want here to indicate
      // that the content was updated
      $this.addClass( 'editable_updated' ); // green background + white text
      setTimeout(function() {
       $this.removeClass( 'editable_updated' );
      }, 500);

      // When enter is hit on an editable field (Assigned, Expiration, etc)
      // it will start here.
      $.post("/form.php",
        {
          host: this.dataset.name,
          data: this.innerText,
          id: this.id
        },
        function(result){
          alert(result);
        }
      );

    });

  $('button').click(function() {
    var $t = $(this),
    col = $t.data('filter-column'), // zero-based index
    filter = [];

    filter[col] = $t.text(); // text to add to filter
    $('#filters').trigger('search', [ filter ]);
    return false;
  });
        
  $('#popover').popover({
    placement: 'right',
    html: true, // required if content has HTML
    content: '<div id="popover-target"></div>'
  })
  
  .on('shown.bs.popover', function () {
    $.tablesorter.columnSelector.attachTo( $('.bootstrap-popup'), '#popover-target');
  });
});


