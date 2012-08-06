function getTagsNames(){
  var res=new Array();
  var tmp=null;
  for(var a=1;a<arguments.length;a++){
    tmp=arguments[0].getElementsByTagName(arguments[a]);
    for(var t=0;t<tmp.length;t++)
      res.push(tmp[t]);
  }
  return res;
}
function getServices(){
  var res=new Array();
  var tmp=null;
  for(var a=1;a<arguments.length;a++){
    tmp=arguments[0].getElementById(arguments[a]);
	var services=tmp.innerHTML.split("\n");
	for (var i=0;i<services.length;i++){if (services[i]) { res.push(services[i]);}}
  }
  return res;
}

var hidden=false;

function splitServices(){
	var tables=document.getElementsByTagName("table");
    for (var t=0;t<tables.length; t++) {
        var services=tables[t].getElementsByTagName("tr")[0].getElementsByTagName("th");
		for (var s=0; s<services.length;s++) {               
			 services[s].setAttribute("colspan",1);
             services[s].style.display='';
		}
    }
}

function joinServices(){
	var tables=document.getElementsByTagName("table");
	for (var t=0;t<tables.length; t++) {
		var services=tables[t].getElementsByTagName("tr")[0].getElementsByTagName("th");
		var s=1;
		while(s<services.length){
			if (services[s].style.display.match("none")) {
				s++;
				continue;
			}
			var i=1;
			while ((s+i<services.length) && (services[s].innerHTML.match(services[s+i].innerHTML))){
				if (services[s+i].style.display.match("none")){
					i++;
					continue;
				}
				var colspan=services[s].getAttribute("colspan");
				if (colspan) { colspan++;}
				else { colspan=2;}
				services[s].setAttribute("colspan",colspan);
				services[s+i].style.display="none";
				i++;
			}
			s=s+i;
		}
	}
}

var showed=0;

function showBad(){
	splitServices();
//	if (hidden) {return;}
//	else {
	var tables = document.getElementsByTagName("table");
	for (var t=0; t< tables.length; t++){
		var elems=getTagsNames(tables[t],"td","th");
		for (var i=0;i<elems.length;i++){
			var name = elems[i].getAttribute("name")
			if (name && name.match("time")) {continue;}
			elems[i].style.display='none';
		}
		var rows=tables[t].getElementsByTagName("tr");
		var services=rows[0].getElementsByTagName("th");
		var machines=rows[1].getElementsByTagName("th");
		for (var r=2;r<rows.length;r++){
			var cells = rows[r].getElementsByTagName("td");
			for (var c = 0; c<cells.length; c++){
				if (cells[c].getAttribute("name").match("WARN") || cells[c].getAttribute("name").match("ERROR")) {
					cells[c].style.display='';
					for (var j=2;j<rows.length;j++){
						rows[j].getElementsByTagName("td")[c].style.display='';
					}
					rows[r].getElementsByTagName("th")[0].style.display='';
					rows[0].style.display='';
					services[0].style.display='';
					rows[1].style.display='';
					rows[r].style.display='';
					machines[0].style.display='';
					machines[c+1].style.display='';
					services[c+1].style.display='';
				}
			}
		}
		var cells=tables[t].getElementsByTagName("td");
		var i=0;
		for (i=0;i<cells.length;i++){
			if (!cells[i].style.display.match("none")) {break;}
		}
		if (i==cells.length) {
			tables[t].style.display='none';
		} 
//	}
//	joinServices()
//	hidden=true;
	showed=0;
//	if (showed==1) {Category("indexes");}
//	if (showed==2) { Category("fronts");}
//	if (showed==3) { Category("etc");}
//	if (showed==4) {Category("handlers");}
	}
	joinServices();
}
	
function showAll(){
	location.reload();
}


Array.prototype.contains = function(obj) {
    var i = this.length;
    while (i--) {
        if (this[i] === obj) {
            return true;
        }
    }
    return false;
}

function Category(cat) {
	splitServices();
	switch (cat) {
		case "indexes":
			showed=1;
			break;
		case "fronts":
			showed=2;
			break;
		case "etc":
			showed=3;
			break;
		case "handlers":
			showed=4;
			break;
	}
	if (showed==3) {
		var showedservices = getServices(document,"indexes","fronts","handlers");
		var hide='';
		var show='none';
	}
	else {
		var showedservices = getServices(document,cat);
		var hide='none';
		var show='';
	}
	var tables = document.getElementsByTagName("table");
    for (var t=0; t< tables.length; t++){
        var rows=tables[t].getElementsByTagName("tr");
        var services=rows[0].getElementsByTagName("th");
        var machines=rows[1].getElementsByTagName("th");
		for (var s=1; s<services.length; s++){
			var service=services[s].getElementsByTagName("span")[0].innerHTML;
			if (!showedservices.contains(service)) {
				services[s].style.display=hide;
				machines[s].style.display=hide;
				for (var r=2;r<rows.length;r++){
					rows[r].getElementsByTagName("td")[s-1].style.display=hide;
				}
			}
			else {
				services[s].style.display=show;
				machines[s].style.display=show;
				for (var r=2;r<rows.length;r++){
                    rows[r].getElementsByTagName("td")[s-1].style.display=show;
                }
			}
		}
		var cells=tables[t].getElementsByTagName("td");
        var i=0;
        for (i=0;i<cells.length;i++){
            if (!cells[i].style.display.match("none")) {break;}
        }
        if (i==cells.length) {
            tables[t].style.display='none';
        }
	}
	joinServices();
}

function highLight(oObject,fl) {
	var cells=getTagsNames(oObject,"th","td");
	if (fl==1) {
	//	if (oObject.style.backgroundColor=="#d0e5e5") {return;}
		oObject.style.backgroundColor="#d1e6e7";
	}
	//else if (fl==2) {
	//	if (oObject.style.backgroundColor=="#d0e5e5") {oObject.style.backgroundColor="";}
	//	oObject.style.backgroundColor="#d0e5e5";
	//}
	else {
	//	if (oObject.style.backgroundColor=="#d0e5e5") {return;}
		oObject.style.backgroundColor="";
	}
	for (var c=0; c<cells.length;c++) {
		if (fl==1) {
	//		if (cells[c].style.backgroundColor=="#d0e5e5") {break;}
		//else 
		if (cells[c].getAttribute("name").match("WARN") || cells[c].getAttribute("name").match("ERROR")) {continue;}
		else {	cells[c].style.backgroundColor="#d1e6e7"; }
		}
		//else if (fl==2) {
		//	if (cells[c].style.backgroundColor==="#d0e5e5") {cells[c].style.backgroundColor="";}
		//	else if (cells[c].getAttribute("name").match("WARN") || cells[c].getAttribute("name").match("ERROR")) 
		//			{continue;}
		//	else { cells[c].style.backgroundColor="#d0e5e5";	}
		//}
		else {
		//	if (cells[c].style.backgroundColor==="#d0e5e5") {break;}
			cells[c].style.backgroundColor="";
		}
	}
}
