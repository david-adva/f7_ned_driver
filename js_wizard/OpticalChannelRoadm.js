dojo.provide("webgui.application.wizard.OpticalChannelRoadm");
dojo.declare("webgui.application.wizard.OpticalChannelRoadm",null,{constructor:function(_1){
var _2=this;
_2.channelFilter="vNoFilter";
_2.connectionType2FromPortside={add:"Cx",drop:"N",addDrop:"N",steerableAdd:"N",steerableDrop:"N",steerableAddDrop:"N",passThru:"N"};
_2.direction2Conn={"1way":"UNI","2way":"BI"};
_2.crossInfo2ConfigCrs={passThru:"PASS",addDrop:"ADD-DROP",add:"ADD",drop:"DROP",steerableAddDrop:"STRBL-ADD-DROP",steerableAdd:"STRBL-ADD",steerableDrop:"STRBL-DROP"};
_2.crossInfo=[{value:"passThru",img:"passthroughtwoway",direction:"2way",mode:"N-FIXED"},{value:"addDrop",img:"adddrop",direction:"2way",mode:"N-FIXED"},{value:"steerableAddDrop",img:"steerableadddrop",direction:"2way"},{value:"passThru",img:"passthroughoneway",direction:"1way",mode:"N-FIXED"},{value:"add",img:"plainadd",direction:"1way",mode:"N-FIXED"},{value:"drop",img:"plaindrop",direction:"1way",mode:"N-FIXED"},{value:"steerableDrop",img:"steerabledrop",direction:"1way",mode:"N-FIXED"},{value:"steerableAdd",img:"steerableadd",direction:"1way",mode:"C-SELECT"}];
_2.mainContainer=new dijit.layout.ContentPane();
_2.item=_1.itemObj;
_2.equipmentType=_2.item.type[0];
_2.modAddress=_2.item.address[0];
_2.wizardDialogTitle="Wizard for optical channel - "+_2.equipmentType;
_2.mainDialog=webgui.widget.Dialog({title:_2.wizardDialogTitle,draggable:true,duration:300,style:"width: 600px;",reposition:function(){
var h=dojo.marginBox(this.domNode).h;
var wH=dojo.window.getBox().h;
if(h>wH){
var gH=wH-100;
dojo.style(_2.mainContainer.domNode,"height",gH+"px");
}
this.layout();
}});
_2.setLoading(true);
_2.mainDialog.show();
_2.mainContainer.startup();
_2.mainDialog.set("content",_2.mainContainer.domNode);
_2.configDetailsPane=dojo.create("ul",{"class":"configDetailsPane"});
_2.mainContainer.addChild(_2.configDetailsPane);
var li=dojo.create("li",{},_2.configDetailsPane);
var _3=dojo.create("div",{"class":"paramLabel"},li);
var _4=dojo.create("div",{"class":"paramWidget"},li);
var _5=dojo.create("label",{innerHTML:"Add Channel:"},_3);
var _6=function(_7){
if(_7.error){
_2.onGenericError(_7);
}else{
if(_7.parameters.length&&_7.parameters[0].keyword=="MODE"){
if(_7.parameters[0].error=="NOT_SUPPORTED"){
_2.mainDialog.hide();
_2.mainDialog.destroyRecursive();
new webgui.dynamic_app_view.PromptMessage({subAppId:"deletedmodule",title:"Error",msg:"Required module "+_2.modAddress+" deleted",displayCancel:false,icon:"error",callback:function(){
return;
},popupWidth:350});
return;
}
var _8=webgui.utils.decode(_7.parameters[0].value);
if(dojo.indexOf(["C-SELECT","N-FIXED"],_8)===-1){
_2.mainDialog.hide();
_2.mainDialog.destroyRecursive();
new webgui.dynamic_app_view.PromptMessage({subAppId:"notselectedmodule",title:"Error",msg:"Module mode has not been selected",displayCancel:false,icon:"error",callback:function(){
return;
},popupWidth:350});
return;
}
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/addresses_config"),content:{originAddress:_2.modAddress,aidGroup:"AIDNAME_OM",relation:"same-slot-by-pvalue",paramKeyword:"ADMIN",paramValue:"AINS|IS|MGT|MT"},handleAs:"json",load:function(_9){
var _a=false,_b=false;
dojo.forEach(_9.addresses,function(_c){
_a=_a||/C\d$/.test(_c);
_b=_b||/N$/.test(_c);
});
if(!(_a&&_b)){
_2.mainDialog.hide();
_2.mainDialog.destroyRecursive();
new webgui.dynamic_app_view.PromptMessage({subAppId:"nonandcport",title:"",msg:"The N port and a least one C port must be added and the ports Admin State must be set to Management, Maintenance, Auto In Service or In Service. ",displayCancel:false,callback:function(){
return;
},popupWidth:350});
return;
}
var _d=[{label:"-- select --",value:null}];
dojo.forEach(_2.crossInfo,function(_e,i){
if(!_e.hasOwnProperty("mode")||_e.mode==_8){
_d.push({label:"<img  style=\"vertical-align:middle;padding:0;width:250px;height:95px;\" src=\"images/crossimg/"+_e.img+".png\" alt=\""+_e.value+"\" />",value:[_e.value,"-",_e.direction].join("")});
}
});
_2.selectCrossType=new dijit.form.Select({id:"_wizard:crossType",options:_d,style:"width: 285px;float:middle",onChange:dojo.hitch(_2,_2.getFromPoint),maxHeight:400});
dojo.place(_2.selectCrossType.domNode,_4);
_2.setLoading(false);
}});
}
}
};
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/system_read_config?")+webgui.utils.paramId(_2.modAddress,"MODE"),handleAs:"json",load:_6});
var _f=new dijit.layout.ContentPane({style:"width: 100%;"});
_2.addBtn=new dijit.form.Button({id:"_wizard;add",label:"Add",style:"margin-top: 10px; float: left;",disabled:true,onClick:dojo.hitch(_2,_2.addCrossConection)});
_f.addChild(_2.addBtn.domNode);
var _10=dojo.create("a",{id:"_wizard;cancel",href:"#",tabIndex:0,"class":"link nodeSnmpLink",innerHTML:"Cancel",onclick:function(e){
dojo.stopEvent(e);
_2.mainDialog.hide();
_2.mainDialog.destroyRecursive();
}});
_f.addChild(_10);
_2.mainContainer.addChild(_f.domNode);
_2.chaSpc=_2.getModuleChaSpc(_2.modAddress,false);
},getModuleChaSpc:function(_11,_12){
var _13=this;
var _14="unknown";
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/system_read_config?")+webgui.utils.paramId(_11,"CHA__SPC"),handleAs:"json",sync:_12,load:function(_15){
if(_15.error){
_13.onGenericError(_15);
}else{
if(_15.parameters.length&&_15.parameters[0].keyword=="CHA__SPC"){
if(_15.parameters[0].error=="NOT_SUPPORTED"){
_13.mainDialog.hide();
_13.mainDialog.destroyRecursive();
new webgui.dynamic_app_view.PromptMessage({subAppId:"deletedmodule",title:"Error",msg:"Required module "+_11+" deleted",displayCancel:false,icon:"error",callback:function(){
return;
},popupWidth:350});
return;
}
if(_12==true){
_14=webgui.utils.decode(_15.parameters[0].value);
}else{
_13.chaSpc=webgui.utils.decode(_15.parameters[0].value);
}
}
}
}});
return _14;
},getFromPoint:function(){
var _16=this;
_16.setLoading(true);
_16.destroyFromPoint();
_16.destroyChannelFilter();
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/addresses_config"),content:{originAddress:_16.modAddress,aidGroup:"AIDNAME_OM",portSide:_16.connectionType2FromPortside[_16.selectCrossType.get("value").split("-")[0]],entityState:"AS"},handleAs:"json",load:function(_17){
if(_17.error){
_16.onGenericError(_17);
}else{
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/system_read_config?")+webgui.xhrParam(_17.addresses,"ADMIN"),handleAs:"json",load:function(_18){
var _19=(_18.parameters.length===1)?[]:[{label:"-- select --",value:null}];
var _1a=dojo.filter(_18.parameters,function(_1b){
return _1b.value!="DSBLD";
});
if(!_1a.length){
new webgui.dynamic_app_view.PromptMessage({subAppId:"nonandcport",title:"",msg:"The N port and a least one C port must be added and the ports Admin State must be set to Management, Maintenance, Auto In Service or In Service. ",displayCancel:false,callback:function(){
return;
},popupWidth:350});
_16.setLoading(false);
}else{
var _1c=dojo.map(_1a,function(_1d){
return _1d.address;
});
dojo.forEach(_1c,function(_1e){
_19.push({label:_1e.replace("OM-","")+" ("+_16.chaSpc+")",value:webgui.utils.decode(_1e)});
});
var _1f={id:"_wizard:fromPoint",options:_19,style:"width: 285px;float:middle",onChange:dojo.hitch(_16,_16.getToPoint),maxHeight:100};
var ret=_16.createParamRow({labelStr:"(A) Local Port:","selectOptions":_1f});
_16.selectFromLi=ret.li;
_16.selectFrom=ret.select;
_16.setLoading(false);
if(_1c.length===1){
_16.getToPoint();
}
}
}});
}
}});
},getToPoint:function(){
var _20=this;
_20.setLoading(true);
_20.destroyToPoint();
_20.destroyChannelFilter();
var _21=function(_22){
if(_22.error){
if(_22.error=="STATE"){
new webgui.dynamic_app_view.PromptMessage({subAppId:"conectedtoanotherroadm",title:"Error",msg:"Selected port is connected to another ROADM module. Select a different channel type or port.",displayCancel:false,icon:"error",callback:function(){
return;
},popupWidth:350});
_20.selectFrom.getOptions(_20.selectFrom.get("value")).disabled=true;
_20.selectFrom.startup();
_20.setLoading(false);
}else{
_20.onGenericError(_22);
}
}else{
var _23=_20.getUniqueToOptions(_22);
if(!_23.length){
new webgui.dynamic_app_view.PromptMessage({subAppId:"routenotavailable",title:"",msg:"Route not available for selected port. Select a different channel type, channel or port.",displayCancel:false,callback:function(){
return;
},popupWidth:350});
_20.setLoading(false);
return;
}
var _24={id:"_wizard:toPoint",options:_23,style:"width: 285px;float:middle",onChange:dojo.hitch(_20,_20.getCaps),maxHeight:100};
var ret=_20.createParamRow({labelStr:"(B) Linked Port:","selectOptions":_24});
_20.selectToLi=ret.li;
_20.selectTo=ret.select;
_20.setLoading(false);
if(_23.length===1){
_20.getCaps();
}
}
};
var _25={};
_25[webgui.xhrParam("NE","FROM-AID")]=_20.selectFrom.get("value");
_25[webgui.xhrParam("NE","CONN")]=_20.direction2Conn[_20.selectCrossType.get("value").split("-")[1]];
_25[webgui.xhrParam("NE","CONFIG__CRS")]=_20.crossInfo2ConfigCrs[_20.selectCrossType.get("value").split("-")[0]];
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/ease_of_use_crs_create_config"),content:_25,handleAs:"json",load:_21});
},getCaps:function(){
var _26=this;
_26.setLoading(true);
_26.destroyChannelFilter();
_26.destroyCaps();
var _27=function(_28){
if(_28.error){
_26.onGenericError(_28);
}else{
if(!_28.parameters||!_28.parameters.length){
new webgui.dynamic_app_view.PromptMessage({subAppId:"nochanelavailable",title:"",msg:"No channels available for selected route. Select a different connection type or different route.",displayCancel:false,callback:function(){
return;
},popupWidth:350});
_26.setLoading(false);
}else{
_26.response=_28;
_26.createChannelFilter();
_26.selectCaps=_26.createParamRows(_28);
_26.setLoading(false);
_26.validateAllParams();
}
}
};
var _29={};
_29[webgui.xhrParam("NE","FROM-AID")]=_26.selectFrom.get("value");
_29[webgui.xhrParam("NE","CONN")]=_26.direction2Conn[_26.selectCrossType.get("value").split("-")[1]];
_29[webgui.xhrParam("NE","CONFIG__CRS")]=_26.crossInfo2ConfigCrs[_26.selectCrossType.get("value").split("-")[0]];
_29[webgui.xhrParam("NE","EP_CRS_TO_AID_LIST")]=_26.selectTo.get("value");
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/ease_of_use_crs_create_config"),content:_29,handleAs:"json",load:_27});
},updateCaps:function(){
var _2a=this;
var _2b=function(_2c){
if(_2c.error){
_2a.onGenericError(_2c);
}else{
if(!_2c.parameters||!_2c.parameters.length){
new webgui.dynamic_app_view.PromptMessage({subAppId:"nobandwidthavailable",title:"",msg:"No bandwidth available for selected channel. Select a different channel.",displayCancel:false,callback:function(){
return;
},popupWidth:350});
_2a.setLoading(false);
}else{
_2a.response=_2c;
_2a.selectCaps=_2a.createParamRows(_2c);
_2a.setLoading(false);
_2a.validateAllParams();
}
}
};
var _2d={};
_2d[webgui.xhrParam("NE","FROM-AID")]=_2a.selectFrom.get("value");
_2d[webgui.xhrParam("NE","CONN")]=_2a.direction2Conn[_2a.selectCrossType.get("value").split("-")[1]];
_2d[webgui.xhrParam("NE","CONFIG__CRS")]=_2a.crossInfo2ConfigCrs[_2a.selectCrossType.get("value").split("-")[0]];
_2d[webgui.xhrParam("NE","EP_CRS_TO_AID_LIST")]=_2a.selectTo.get("value");
dojo.forEach(_2a.selectCaps,function(cap){
var _2e=cap.select.get("name");
if(_2e==webgui.xhrParam("NE","CHANNEL__PROVISION")){
var _2f=cap.select.get("value");
_2d[_2e]=_2f;
}
});
_2a.destroyCaps();
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/ease_of_use_crs_create_config"),content:_2d,handleAs:"json",load:_2b});
},addCrossConection:function(){
var _30=this;
var _31=function(_32){
if(_32.error){
var msg="";
var _33=webgui.utils.parameterListToObject(_32.parameters,"keyword");
switch(_32.error){
case "EXISTENT_ADDRESS":
msg="Entity already exists in the system";
break;
case "NONEXISTENT_ADDRESS":
if(_33&&_33.ERRAID){
var _34=webgui.utils.decode(_33.ERRAID.value);
if(/^MOD-/.test(_34)){
msg="Required module "+_34+" deleted.";
}else{
if(/^OM-/.test(_34)){
msg="Required port "+_34+" deleted.";
}else{
msg="Required entity "+_34+" deleted.";
}
}
}else{
_30.onGenericError(_32);
return;
}
break;
case "CREATION_FAILURE":
if(_33&&_33.ERRAID){
msg="Channel resource in use, endpoint "+_33.ERRAID.value+" exists.";
}else{
_30.onGenericError(_32);
return;
}
break;
case "STATE":
if(_33&&_33.ERRAID){
var _34=webgui.utils.decode(_33.ERRAID.value);
msg="One ("+_34+") or more of the ports required to add the channel Admin State is set to Disabled.                                Set the Admin State for all required ports to Management, Maintenance, Auto In Service or In Service.";
}else{
_30.onGenericError(_32);
return;
}
break;
default:
_30.onGenericError(_32);
return;
}
new webgui.dynamic_app_view.PromptMessage({subAppId:"addcrossconnectionerror",title:"Error",msg:msg,displayCancel:false,icon:"error",callback:function(){
return;
},popupWidth:350});
_30.setLoading(false);
}else{
webgui.utils.msg.message("Connection was created");
dojo.publish("/reload/config/openPanes");
_30.mainDialog.hide();
_30.mainDialog.destroyRecursive();
}
};
var _35={};
_35[webgui.xhrParam("NE","FROM-AID")]=_30.selectFrom.get("value");
_35[webgui.xhrParam("NE","CONN")]=_30.direction2Conn[_30.selectCrossType.get("value").split("-")[1]];
_35[webgui.xhrParam("NE","CONFIG__CRS")]=_30.crossInfo2ConfigCrs[_30.selectCrossType.get("value").split("-")[0]];
_35[webgui.xhrParam("NE","EP_CRS_TO_AID_LIST")]=_30.selectTo.get("value");
dojo.forEach(_30.selectCaps,function(cap){
var _36=cap.select.get("name");
var _37=cap.select.get("value");
_35[_36]=_37;
});
dojo.xhrPost({url:webgui.utils.proxyUrl("/scripts/ease_of_use_crs_create_config"),content:_35,handleAs:"json",load:_31});
},validateAllParams:function(){
var _38=this;
_38.allParamsValid=dojo.every(_38.selectCaps,function(cap){
return cap.select.validate();
});
_38.addBtn.set("disabled",!_38.allParamsValid);
},createParamRow:function(_39){
var _3a=this;
var ret=[];
if(_39.selectOptions){
var li=dojo.create("li",{},_3a.configDetailsPane);
var _3b=dojo.create("div",{"class":"paramLabel"},li);
var _3c=dojo.create("label",{innerHTML:_39.labelStr},_3b);
var _3d=dojo.create("div",{"class":"paramWidget"},li);
var _3e=new dijit.form.Select(_39.selectOptions);
dojo.place(_3e.domNode,_3d);
ret={"li":li,"select":_3e};
}
return ret;
},createParamRows:function(_3f){
var _40=this;
var ret=[];
dojo.forEach(_3f.parameters,function(_41){
var li=dojo.create("li",{},_40.configDetailsPane);
var _42=dojo.create("div",{"class":"paramLabel"},li);
var _43=webgui.utils.parameterName(_41)+":";
if(_41.keyword=="PATH-NODE"){
_43="(A &#8594; B) "+_43;
}else{
if(_41.keyword=="PATH-NODE__REVERSE"){
_43="(B &#8594; A) "+_43;
}
}
var _44=dojo.create("label",{innerHTML:_43},_42);
var _45=dojo.create("div",{"class":"paramWidget"},li);
var _46;
if(_41.keyword=="CHANNEL__PROVISION"){
var _47=_40.filterChannels(_41);
_46=webgui.utils.createDynamicWidget(_47);
}else{
_46=webgui.utils.createDynamicWidget(_41);
}
_46.onChange=dojo.hitch(_40,_40.validateAllParams);
dojo.place(_46.domNode,_45);
ret.push({"li":li,"select":_46});
if(_41.keyword=="CHANNEL__PROVISION"){
if(_40.chaSpc=="FLEX"){
_46.onChange=dojo.hitch(_40,_40.updateCaps);
}
}
});
return ret;
},getUniqueToOptions:function(_48){
var _49=this;
var _4a=[];
dojo.forEach(_48.parameters,function(_4b){
if(_4b.keyword==="EP_CRS_TO_AID_LIST"&&_4b.options.length){
if(_4b.options.length>1){
_4a=[{label:"-- select --",value:null}];
}
if(_4b.options[0].indexOf("&")>-1){
var _4c={};
dojo.forEach(_4b.options,function(_4d){
var _4e=_4d.split("&");
var _4f=_4e[_4e.length-1];
var _50=_4e.slice(0,_4e.length-1);
if(_4c.hasOwnProperty(_4f)){
_4c[_4f].routes.push(_50);
}else{
_4c[_4f]={routes:[_50,]};
}
});
var _51=function(_52,_53){
var _54=_53.length>1;
dojo.forEach(_53,function(_55){
var _56=_54?"("+dojo.map(_55,function(aid){
return aid.replace(/OM-\d+-\d+-/gi,"");
}).join(",")+") ":" ";
var _57=_55.concat(_52).join("&");
var _58=_52.replace("/OM-d+-d+-/gi","MOD-d+-d");
var _59=_49.getModuleChaSpc(_58,true);
_4a.push({label:_56+_52.replace("OM-","")+" ("+_59+")",value:_57});
});
};
for(var _5a in _4c){
_51(_5a,_4c[_5a].routes);
}
}else{
dojo.forEach(_4b.options,function(_5b){
var _5c=_5b.replace("/OM-d+-d+-/gi","MOD-d+-d");
var _5d=_49.getModuleChaSpc(_5c,true);
_4a.push({label:_5b.replace("OM-","")+" ("+_5d+")",value:webgui.utils.decode(_5b)});
});
}
}
});
return _4a;
},destroyFromPoint:function(){
var _5e=this;
if(_5e.selectFromLi){
_5e.destroyToPoint();
_5e.selectFrom.destroy();
dojo.destroy(_5e.selectFromLi);
}
},destroyToPoint:function(){
var _5f=this;
if(_5f.selectToLi){
_5f.destroyCaps();
_5f.selectTo.destroy();
dojo.destroy(_5f.selectToLi);
}
},destroyCaps:function(){
var _60=this;
_60.addBtn.set("disabled",true);
dojo.forEach(_60.selectCaps,function(_61){
_61.select.destroy();
dojo.destroy(_61.li);
});
},setLoading:function(val){
var _62=this;
_62.mainDialog.set("loading",val);
var _63=[_62.selectCrossType,_62.selectFrom,_62.selectTo];
_63.join(_62.selectCaps);
dojo.forEach(_63,function(_64){
if(_64&&!_64.get("_destroyed")){
var _65=(_64.options.length>1)?val:true;
_64.set("disabled",_65);
}
});
},onGenericError:function(_66){
var _67=this;
new webgui.dynamic_app_view.PromptMessage({subAppId:"genericerror",title:"Error",msg:webgui.utils.errorCodeToMessage(_66.error)+",<br/>"+_66.errorMessage,displayCancel:false,icon:"error",callback:function(){
return;
},popupWidth:350});
_67.setLoading(false);
},createChannelFilter:function(){
var _68=this;
_68.ulChannelFilter=dojo.create("ul",{},_68.configDetailsPane);
var _69=dojo.create("label",{"innerHTML":"Channel Range : &nbsp"},_68.ulChannelFilter);
var li1=dojo.create("li",{"style":"display: inline"},_68.ulChannelFilter);
var li2=dojo.create("li",{"style":"display: inline"},_68.ulChannelFilter);
var li3=dojo.create("li",{"style":"display: inline"},_68.ulChannelFilter);
var li4=dojo.create("li",{"style":"display: inline"},_68.ulChannelFilter);
var li5=dojo.create("li",{"style":"display: inline"},_68.ulChannelFilter);
var li6=dojo.create("li",{"style":"display: inline"},_68.ulChannelFilter);
var _6a=new dijit.form.RadioButton({id:"idNoFilter",checked:(_68.channelFilter=="vNoFilter"),value:"vNoFilter",name:"NoFilter",onChange:dojo.hitch(_6a,_68.radioOnChange,_68)});
var _6b=dojo.create("label",{"for":"noFilterRadio","innerHTML":"All &nbsp &nbsp"});
dojo.place(_6a.domNode,li1);
dojo.place(_6b,li1);
var _6c=new dijit.form.RadioButton({id:"id19500",checked:(_68.channelFilter=="v19500"),value:"v19500",name:"C19500",onChange:dojo.hitch(_6c,_68.radioOnChange,_68)});
var _6d=dojo.create("label",{"for":"C19500Radio","innerHTML":"19500&#8593 &nbsp &nbsp"});
dojo.place(_6c.domNode,li2);
dojo.place(_6d,li2);
var _6e=new dijit.form.RadioButton({id:"id19400",checked:(_68.channelFilter=="v19400"),value:"v19400",name:"C19400",onChange:dojo.hitch(_6e,_68.radioOnChange,_68)});
var _6f=dojo.create("label",{"for":"C19400Radio","innerHTML":"19400&#8593 &nbsp &nbsp"});
dojo.place(_6e.domNode,li3);
dojo.place(_6f,li3);
var _70=new dijit.form.RadioButton({id:"id19300",checked:(_68.channelFilter=="v19300"),value:"v19300",name:"C19300",onChange:dojo.hitch(_70,_68.radioOnChange,_68)});
var _71=dojo.create("label",{"for":"C19300Radio","innerHTML":"19300&#8593 &nbsp &nbsp"});
dojo.place(_70.domNode,li4);
dojo.place(_71,li4);
var _72=new dijit.form.RadioButton({id:"id19200",checked:(_68.channelFilter=="v19200"),value:"v19200",name:"C19200",onChange:dojo.hitch(_68.C19200Radio,_68.radioOnChange,_68)});
var _73=dojo.create("label",{"for":"C19200Radio","innerHTML":"19200&#8593 &nbsp &nbsp"});
dojo.place(_72.domNode,li5);
dojo.place(_73,li5);
var _74=new dijit.form.RadioButton({id:"id19125",checked:(_68.channelFilter=="v19125"),value:"v19125",name:"C19125",onChange:dojo.hitch(_74,_68.radioOnChange,_68)});
var _75=dojo.create("label",{"for":"C19125Radio","innerHTML":"19125&#8593"});
dojo.place(_74.domNode,li6);
dojo.place(_75,li6);
_68.channelFilterOptions=[_6a,_6c,_6e,_70,_72,_74];
},radioOnChange:function(_76){
var _77=this;
var _78="";
_78=_77.get("value");
if((_78!="")&&(_78!=_76.channelFilter)){
_76.channelFilter=_78;
_76.destroyChannelFilter();
_76.destroyCaps();
_76.createChannelFilter();
_76.selectCaps=_76.createParamRows(_76.response);
_76.setLoading(false);
_76.validateAllParams();
}
},destroyChannelFilter:function(){
var _79=this;
dojo.forEach(_79.channelFilterOptions,function(_7a){
dojo.destroy(_7a.li);
_7a.destroy();
});
dojo.destroy(_79.ulChannelFilter);
},filterChannels:function(_7b){
var _7c=this;
var _7d;
switch(_7c.channelFilter){
case "v19500":
_7d=_7c.filterRange(_7b,19500,19601);
break;
case "v19400":
_7d=_7c.filterRange(_7b,19400,19500);
break;
case "v19300":
_7d=_7c.filterRange(_7b,19300,19400);
break;
case "v19200":
_7d=_7c.filterRange(_7b,19200,19300);
break;
case "v19125":
_7d=_7c.filterRange(_7b,19125,19200);
break;
case "vNoFilter":
default:
_7d=_7b;
break;
}
return _7d;
},filterRange:function(_7e,_7f,_80){
var _81=this;
var _82={};
_82.address=_7e.address;
_82.keyword=_7e.keyword;
_82.value=_7e.value;
_82.enabled=_7e.enabled;
_82.options=[];
if(_7e.options.length>1){
dojo.forEach(_7e.options,function(_83){
if((_83>=_7f)&&(_83<_80)){
_82.options.push(_83);
}
});
}
_82.complete=_7e.complete;
return _82;
}});

