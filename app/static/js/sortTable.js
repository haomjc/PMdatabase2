
var allNums = false;        // boolean variable to see if whole column is numeric
var allDates = false;        // boolean variable to see if column vals are all dates
var compValue = false;		// boolean variable to see if column vals contain a mix of text and numerical
var lastSort = -1;                // variable to hold last column number sorted
var absOrder = true;        // boolean to sort in reverse if on same column
var customSortb = false;
var tableID = "datatable";
var lastClick = "";
//-----------------------------------------------------------------------
function setDataType(inValue) {
    // This function checks data type of a value
    //         - sets allNums to false if a non-number is found
    //        - sets allDates to false if a non-date is found

    if (isNaN(inValue)) {
		// It is a date or a string
    	var isDate = new Date(inValue);
    	if (isDate == "NaN" || isDate == "Invalid Date") {
			if (customSortb == true){
				// value is composite
				invalue = inValue;
				allNums = false
				allDates = false
				return inValue;
			}
			else
			{
			   // The value is a string - make all characters in
			   // String upper case to assure proper a-z sort
			   inValue =  inValue.toUpperCase();
			   allNums = false
			   allDates = false
				compValue = false
			   return inValue;
			}
		} else {
			// Value to sort is a date
			allNums = false
			compValue = false
			return inValue ;
		}

	} else {
        // Value is a number, make sure it is not treated as a string
        allDates = false
	    compValue = false
        return parseFloat(1*inValue);
	}

  }
//-----------------------------------------------------------------------

function customSort1(col)
{
	customSortb = true;
	doSortTable(col,"datatable");
}
function customSort2(col,tableIDval)
{
	customSortb = true;
	doSortTable(col,tableIDval);
}
function sortTable1(col){
	customSortb = false;
	try{
	doSortTable(col,"datatable");
	}
	catch(everything){}
}
function sortTable2(col,tableIDval)
{
	customSortb = false;
	try{
		doSortTable(col,tableIDval);
	}
	catch(everything){}
}
function doSortTable(col,tableIDval){
		if (lastClick != ""){
		eval("document.images['"+lastClick+"sortimg"+ col + "'].src='../images/spacer.gif';")
		if (lastClick != tableIDval){
			lastSort = -1;
		}
		}
    if (lastSort == col){
        // sorting on same column twice = reverse sort order
        absOrder ? absOrder = false : absOrder = true
	if (absOrder)
	{
		eval("document.images['"+tableIDval+"sortimg"+ col + "'].src='../images/tri-u.gif';")
	}
	else
	{
		eval("document.images['"+tableIDval+"sortimg"+ col + "'].src='../images/tri-d.gif';")
	}

    }
    else{
        absOrder = true
	if (lastSort != -1)
	{
		eval("document.images['"+tableIDval+"sortimg"+ lastSort + "'].src='../images/spacer.gif';")
	}
	eval("document.images['"+tableIDval+"sortimg"+ col + "'].src='../images/tri-u.gif';")
    }
	lastClick = tableIDval;
    lastSort = col
	//alert("tableID + " + tableIDval);
	tableEl = document.getElementById(tableIDval);
	tbodyEl = tableEl.getElementsByTagName("tbody");
	allTR = tbodyEl[0].getElementsByTagName("tr");

    // allTR now holds all the rows in the dataTable
    totalRows = allTR.length
    colToSort = new Array()        	// holds all the cells in the column to sort
    colArr = new Array()                // holds all the rows that correspond to the sort cell
    copyArr = new Array()            	// holds an original copy of the sort data  to match to colArr
    resultArr = new Array()            	// holds the output

    allNums = true
    allDates = true
    compValue = true;
    //store the original data
    //remember that the first row - [0] -  has column headings
    //so start with the second row - [1]
    //and load the contents of the cell into the array that will be sorted

	// This code is necessary for browsers that don't reflect the DOM
	// constants (like IE).
	if (document.ELEMENT_NODE == null) {
	  	document.ELEMENT_NODE = 1;
 	 	document.TEXT_NODE = 3;
	}


    for (x=0; x < totalRows; x++){
		colToSort[x] = setDataType(getTextValue(allTR[x].childNodes[col]));
        colArr[x] = allTR[x]
    }

    //make a copy of the original
    for (x=0; x<colToSort.length; x++){
        copyArr[x] = colToSort[x]
    }

    //sort the original data based on data type
    if (allNums){
        colToSort.sort(numberOrder)
    }
    else if (allDates){
        colToSort.sort(dateOrder)
    }
    else if (compValue){
	colToSort.sort(userOrder)
    }
    else{
        colToSort.sort(textOrder)
    }
    //match copy to sorted
    for(x=0; x<colToSort.length; x++){
        for(y=0; y<copyArr.length; y++){
            if (colToSort[x] == copyArr[y]){
                boolListed = false
                //search the ouput array to make sure not to use duplicate rows
                for(z=0; z<resultArr.length; z++){
                    if (resultArr[z]==y){
                        boolListed = true
                        break;
                    }
                }
                if (!boolListed){
                    resultArr[x] = y
                    break;
                }
            }
        }
    }

    //now display the results

    for (x=0; x<resultArr.length; x++){

	parentNode = allTR[x].parentNode;
	parentNode.appendChild(colArr[resultArr[x]]);
    }
	// lastClick = tableIDval;
}
// --------------------------------------------------------------------
function getTextValue(el) {

  var i;
  var s;

  // Find and concatenate the values of all text nodes contained
  // within the element.
  s = "";
  for (i = 0; i < el.childNodes.length; i++)
    if (el.childNodes[i].nodeType == document.TEXT_NODE)
      s += el.childNodes[i].nodeValue;
    else if (el.childNodes[i].nodeType == document.ELEMENT_NODE &&
             el.childNodes[i].tagName == "BR")
      s += " ";
    else
      // Use recursion to get text within sub-elements.
      s += getTextValue(el.childNodes[i]);
  return normalizeString(s);
}
// --------------------------------------------------
// Regular expressions for normalizing white space.
var whtSpEnds = new RegExp("^\\s*|\\s*$", "g");
var whtSpMult = new RegExp("\\s\\s+", "g");

function normalizeString(s) {

  s = s.replace(whtSpMult, " ");  // Collapse any multiple whites space.
  s = s.replace(whtSpEnds, "");   // Remove leading or trailing white
                                  // space.
  return s;
}

//-----------------------------------------------------------------------
function numberOrder(a,b){
    // absOrder ? rVal = b - a : rVal = a - b
	absOrder ? rVal = a - b : rVal = b - a
    return rVal
}
//-----------------------------------------------------------------------
function dateOrder(a,b){
    absOrder ? rVal = Date.parse(a) - Date.parse(b) : rVal = Date.parse(b) - Date.parse(a)
    return rVal
}

//-----------------------------------------------------------------------
function textOrder(a,b){
    if (a.toString() < b.toString()){
        absOrder ? rVal = -1 : rVal = 1
    }
    else{
        absOrder ? rVal = 1 : rVal = -1
    }
    return rVal
}