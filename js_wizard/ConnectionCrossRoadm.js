dojo.provide("webgui.application.wizard.ConnectionCrossRoadm");
dojo.declare("webgui.application.wizard.ConnectionCrossRoadm",null,{constructor:function(_1){
var _2=this;
_2.parentAddress=_1.itemObj.address[0];
_2.equipmentType=_1.itemObj.type[0];
_2.roadmNo=_1.roadmNo;
_2.wizardDialogTitle="Wizard for Cross Connection - "+_2.equipmentType;
_2.notAvailable="No Optical Channels available for Cross Connection";
_2.liContainer=[];
_2.roadmMode=null;
_2.roadmModeCDGC=null;
webgui.wizard={};
var _3=new dojo.Deferred();
_2.roadmChannelGroupSupport=(dojo.indexOf(["8ROADM-C80","8ROADM-C40","ROADM-C80","4ROADM-C96"],_2.equipmentType)!==-1);
_2.roadChannelSteerableSupport=(dojo.indexOf(["8ROADM-C80","8ROADM-C40"],_2.equipmentType)!==-1);
_2.roadmPassThruSupport=(dojo.indexOf(["9CCM-C96"],_2.equipmentType)===-1);
_2.roadmTypeCDGC=(dojo.indexOf(["9ROADM-C96","4ROADM-C96","4ROADM-E-C96"],_2.equipmentType)!==-1);
if(dojo.indexOf(["8ROADM-C80","8ROADM-C40","9ROADM-C96","4ROADM-C96","4ROADM-E-C96"],_2.equipmentType)!==-1){
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/system_read_config?")+webgui.xhrParam(_2.parentAddress,"MODE"),handleAs:"json",load:function(_4){
if(_4.parameters.length){
if(_2.roadmTypeCDGC){
_2.roadmModeCDGC=webgui.utils.decode(_4.parameters[0].value);
}else{
_2.roadmMode=webgui.utils.decode(_4.parameters[0].value);
}
}
_3.callback();
}});
}else{
_3.callback();
}
_2.aidGroup="AIDNAME_VCH";
dojo.when(_3,function(){
_2.channelFunction="passThru";
if(_2.roadmMode==="C-SELECT"){
_2.channelFunction="steerableAddDrop";
}
if(_2.roadmModeCDGC==="C-SELECT"){
_2.roadmPassThruSupport=false;
}
if(!_2.roadmPassThruSupport){
_2.channelFunction="addDrop";
}
_2.setupInitView();
dojo.hitch(_2,_2.getUnusedFromPoints)();
});
},getUnusedFromPoints:function(){
var _5=this;
_5.clearView();
var _6="";
if(_5.roadmTypeCDGC){
if(_5.channelFunction==="add"){
_6=(_5.roadmModeCDGC==="C-SELECT")?"Nx":"Cx";
}else{
if(_5.channelFunction==="drop"){
_6=(_5.roadmModeCDGC==="C-SELECT")?"Cx":"Nx";
}
}
}else{
_6=(_5.roadmMode==="C-SELECT"||_5.channelFunction==="add")?"Cx":"Nx";
if(_5.equipmentType==="EROADM-DC"){
if(_5.channelFunction==="add"){
_5.aidGroup="AIDNAME_CH+AIDNAME_CRS_CH";
}else{
_5.aidGroup="AIDNAME_VCH";
}
}
}
dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/addresses_config"),content:{originAddress:_5.parentAddress,relation:"unusedFromPoint",aidGroup:_5.aidGroup,portSide:_6},handleAs:"json",load:dojo.hitch(_5,_5.getFromChannelsInfo)});
},getFromChannelsInfo:function(_7){
var _8=this;
var _9=(_8.aidGroup==="AIDNAME_OTLG")?"LANE-CHANNEL1":"CHANNEL__PROVISION";
var _a=dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/system_read_config?")+webgui.xhrParam(_7.addresses,_9,true),handleAs:"json",load:dojo.hitch(_8,_8.createFromChannel)});
},getChannelOptions:function(_b){
var _c=(_b.length===1)?[]:[{label:"-- select --",value:null}];
dojo.forEach(_b,function(_d){
_c.push({label:_d.valueDisp,value:webgui.utils.decode(_d.value)});
});
return _c;
},setupInitView:function(){
var _e=this;
_e.paneContainer=new dijit.layout.ContentPane({"style":{"width":"500px"},"content":dojo.create("ul",{"class":"configDetailsPane"})});
_e.wizardDialog=new webgui.widget.Dialog({style:"background-color: #fff;",title:_e.wizardDialogTitle,draggable:true,duration:300,reposition:function(){
var h=dojo.marginBox(this.domNode).h;
var wH=dojo.window.getBox().h;
if(h>wH){
var gH=wH-100;
dojo.style(_e.paneContainer.domNode,"height",gH+"px");
}
this.layout();
}});
var _f=new dijit.layout.ContentPane({style:"float: left; width: 50%;"});
_e.submitButton=new dijit.form.Button({id:"_wizard;add",label:"Add",style:"margin-bottom: 10px;margin-left: 10px;",disabled:true,onClick:dojo.hitch(_e,_e.submitButtonClick)});
_f.addChild(_e.submitButton.domNode);
var _10=new dijit.layout.ContentPane({style:"text-align: right;"});
var _11=dojo.create("a",{style:"margin: 10px;",href:"#",tabIndex:0,"class":"link",innerHTML:"Cancel",onclick:function(e){
dojo.stopEvent(e);
_e.wizardDialog.hide();
_e.wizardDialog.destroyRecursive();
}});
_10.addChild(_11);
_e.wizardDialog.set("content",_e.getDirectionPane());
_e.wizardDialog.addChild(_e.getRadioChannelFunction());
_e.wizardDialog.addChild(_e.paneContainer.domNode);
_e.wizardDialog.addChild(_f.domNode);
_e.wizardDialog.addChild(_10.domNode);
_e.wizardDialog.show();
_e.paneContainer.startup();
},clearView:function(arg){
var _12=this;
if(!arg){
var arg={};
}
if(_12.selectFromChannelLi&&!arg.noFromChannelClear){
dojo.destroy(_12.selectFromChannelLi);
_12.selectFromChannel.destroy();
}
if(_12.selectFromLi){
dojo.destroy(_12.selectFromLi);
_12.selectFrom.destroy();
}
if(_12.selectToLi){
dojo.destroy(_12.selectToLi);
_12.selectTo.destroy();
}
dojo.forEach(_12.widgetContainer,function(_13){
_13.destroy();
});
dojo.forEach(_12.liContainer,function(_14){
dojo.empty(_14);
dojo.destroy(_14);
});
_12.liContainer=[];
_12.widgetContainer=[];
_12.submitButton.set("disabled",true);
},createFromChannel:function(_15){
var _16=this;
var _17=_15.parameters||[];
_16.channel2fromPoint={};
var _18=[];
dojo.forEach(_17,function(_19){
var _1a=webgui.utils.decode(_19.valueDisp||_19.value);
if(!_16.channel2fromPoint[_1a]){
_16.channel2fromPoint[_1a]=[_19.address];
_18.push({value:_1a,valueDisp:_1a});
}else{
_16.channel2fromPoint[_1a].push(_19.address);
}
});
_18.sort(_16.sortNatural).reverse();
var _1b=_16.createPortRow({id:"_wizard;channelNumber",parameters:_18,label:"Channel Number",onChange:dojo.hitch(_16,_16.onSelectFromChannelChange)});
_16.selectFromChannelLi=_1b[0];
_16.selectFromChannel=_1b[1];
if(_18.length===1){
_16.selectFromChannel.set("disabled",true);
_16.selectFromChannel.onChange();
}
if(!_17.length){
_16.selectFromChannel.set("disabled",true);
}
},sortNatural:function(a,b){
return webgui.utils.comparator.natural(a.value,b.value);
},onSelectFromChannelChange:function(){
var _1c=this;
_1c.clearView({"noFromChannelClear":true});
var _1d=_1c.selectFromChannel.get("value");
var _1e=[];
var _1f=[];
dojo.forEach(_1c.channel2fromPoint[_1d],function(_20){
var _21;
if(_1c.equipmentType==="EROADM-DC"&&_1c.channelFunction==="add"){
_21=new dojo.Deferred();
_20=_20.replace(/^CH-/,"");
_1f.push(_21);
_21.callback({"addresses":[_20]});
}else{
_21=dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/addresses_config"),handleAs:"json",content:{originAddress:_20,relation:"parent"}});
_1f.push(_21);
}
});
webgui.wizard.localAid2label={};
var xhr=dojo.when(new dojo.DeferredList(_1f),function(_22){
dojo.forEach(_22,function(r,idx){
var _23=r[1].addresses[0];
var _24=_1c.channel2fromPoint[_1d][idx];
var _25=_23.replace(/^OM-/,"");
_1e.push({value:_24,valueDisp:_25});
webgui.wizard.localAid2label[_24]=_25;
});
var _26=_1c.createPortRow({id:"_wizard;localPort",parameters:_1e,label:"(A) Local Port",onChange:dojo.hitch(_1c,_1c.onSelectFromChange)});
_1c.selectFromLi=_26[0];
_1c.selectFrom=_26[1];
if(_1e.length===1){
_1c.selectFrom.set("disabled",true);
_1c.selectFrom.onChange();
}
});
},createPortRow:function(arg){
var _27=this;
var _28=_27.getChannelOptions(arg.parameters);
var _29=_28.length*20;
var _2a=(_29>200)?200:_29;
var _2b=dojo.create("li",{},_27.paneContainer.content);
var _2c=dojo.create("div",{"class":"paramLabel"},_2b);
var _2d=dojo.create("div",{"class":"paramWidget"},_2b);
var _2e=dojo.create("label",{innerHTML:arg.label},_2c);
var _2f=new dijit.form.Select({id:arg.id,maxHeight:_2a,options:_28,onChange:dojo.hitch(_2f,arg.onChange,_27)});
dojo.place(_2f.domNode,_2d);
return [_2b,_2f];
},getDirectionPane:function(){
var _30=this;
var _31=new dijit.layout.ContentPane({style:"margin: 10px"});
var _32=dojo.create("span",{innerHTML:"Direction"});
var _33=[{label:"(A) <-> (B)",value:"2way"},{label:"(A) -> (B)",value:"1way"}];
_30.selectDirection=new dijit.form.Select({id:"_wizard;direction",options:_33,style:"width: 120px; margin: 5px;",onChange:dojo.hitch(_30,_30.onChangeDirection)});
_30.directionValue=_33[0].value;
_31.addChild(_32);
_31.addChild(_30.selectDirection.domNode);
if(_30.roadmChannelGroupSupport){
_30.channelGroup=dijit.form.CheckBox({id:"wizard;channel-group",value:true,style:"margin: 10px;",onChange:function(e){
if(this.get("value")){
_30.aidGroup="AIDNAME_OTLG";
}else{
_30.aidGroup="AIDNAME_VCH";
}
dojo.hitch(_30,_30.getUnusedFromPoints)();
}});
var _34=dojo.create("label",{innerHTML:"Channel Group","for":"wizard;channel-group"});
_31.addChild(_30.channelGroup.domNode);
_31.addChild(_34);
}
return _31;
},onChangeDirection:function(){
var _35=this;
_35.directionValue=_35.selectDirection.get("value");
if(_35.directionValue==="1way"){
dojo.style(_35.addDropLi,"display","none");
dojo.style(_35.steerableAddDropLi,"display","none");
dojo.style(_35.addLi,"display","");
dojo.style(_35.dropLi,"display","");
if(_35.roadChannelSteerableSupport){
dojo.style(_35.steerableAddDropLi,"display","none");
dojo.style(_35.steerableAddLi,"display","");
dojo.style(_35.steerableDropLi,"display","");
}
}else{
if(_35.directionValue==="2way"){
dojo.style(_35.addDropLi,"display","");
dojo.style(_35.addLi,"display","none");
dojo.style(_35.dropLi,"display","none");
if(_35.roadChannelSteerableSupport){
dojo.style(_35.steerableAddDropLi,"display","");
dojo.style(_35.steerableAddLi,"display","none");
dojo.style(_35.steerableDropLi,"display","none");
}
}
}
if(_35.roadChannelSteerableSupport&&_35.roadmMode==="C-SELECT"){
if(_35.directionValue==="1way"){
_35.steerableAddRadio.set("checked",true);
}else{
_35.steerableAddDropRadio.set("checked",true);
}
}else{
if(_35.roadmPassThruSupport){
_35.passThruRadio.set("checked",true);
}else{
if(_35.directionValue==="1way"){
_35.addRadio.set("checked",true);
}else{
_35.addDropRadio.set("checked",true);
}
}
}
},getRadioChannelFunction:function(){
var _36=this;
_36.ulChannelFunction=dojo.create("ul",{});
var li1=dojo.create("li",{"class":"gridOptionsList"},_36.ulChannelFunction);
_36.addDropLi=dojo.create("li",{"class":"gridOptionsList"},_36.ulChannelFunction);
_36.addLi=dojo.create("li",{"style":"display: none;","class":"gridOptionsList"},_36.ulChannelFunction);
_36.dropLi=dojo.create("li",{"style":"display: none;","class":"gridOptionsList"},_36.ulChannelFunction);
_36.steerableAddDropLi=dojo.create("li",{"class":"gridOptionsList"},_36.ulChannelFunction);
_36.steerableAddLi=dojo.create("li",{"style":"display: none;","class":"gridOptionsList"},_36.ulChannelFunction);
_36.steerableDropLi=dojo.create("li",{"style":"display: none;","class":"gridOptionsList"},_36.ulChannelFunction);
if(_36.roadmPassThruSupport){
_36.passThruRadio=new dijit.form.RadioButton({id:"passThruRadio",value:"passThru",name:"channelFunction",checked:(_36.roadmMode!=="C-SELECT"),disabled:(_36.roadmMode==="C-SELECT"),onChange:dojo.hitch(_36.passThruRadio,_36.radioOnChange,_36)});
var _37=dojo.create("label",{"for":"passThruRadio","innerHTML":"Pass-Through"});
dojo.place(_36.passThruRadio.domNode,li1);
dojo.place(_37,li1);
}
_36.addDropRadio=new dijit.form.RadioButton({id:"addDropRadio",value:"addDrop",disabled:(_36.roadmMode==="C-SELECT"),checked:(!_36.roadmPassThruSupport),name:"channelFunction",onChange:dojo.hitch(_36.addDropRadio,_36.radioOnChange,_36)});
var _38=dojo.create("label",{"for":"addDropRadio","innerHTML":"Add-Drop"});
dojo.place(_36.addDropRadio.domNode,_36.addDropLi);
dojo.place(_38,_36.addDropLi);
_36.addRadio=new dijit.form.RadioButton({id:"addRadio",value:"add",disabled:(_36.roadmMode==="C-SELECT"),name:"channelFunction",onChange:dojo.hitch(_36.addRadio,_36.radioOnChange,_36)});
var _39=dojo.create("label",{"for":"addRadio","innerHTML":"Add"});
dojo.place(_36.addRadio.domNode,_36.addLi);
dojo.place(_39,_36.addLi);
_36.dropRadio=new dijit.form.RadioButton({id:"dropRadio",value:"drop",disabled:(_36.roadmMode==="C-SELECT"),name:"channelFunction",onChange:dojo.hitch(_36.dropRadio,_36.radioOnChange,_36)});
var _38=dojo.create("label",{"for":"dropRadio","innerHTML":"Drop"});
dojo.place(_36.dropRadio.domNode,_36.dropLi);
dojo.place(_38,_36.dropLi);
if(_36.roadChannelSteerableSupport){
_36.steerableAddDropRadio=new dijit.form.RadioButton({id:"steerableAddDropRadio",value:"steerableAddDrop",name:"channelFunction",checked:(_36.roadmMode==="C-SELECT"),onChange:dojo.hitch(_36.steerableAddDropRadio,_36.radioOnChange,_36)});
var _3a=dojo.create("label",{"for":"steerableAddDropRadio","innerHTML":"Steerable Add-Drop"});
dojo.place(_36.steerableAddDropRadio.domNode,_36.steerableAddDropLi);
dojo.place(_3a,_36.steerableAddDropLi);
_36.steerableAddRadio=new dijit.form.RadioButton({id:"steerableAddRadio",value:"steerableAdd",name:"channelFunction",checked:(_36.roadmMode==="C-SELECT"),disabled:(_36.roadmMode==="C-SELECT"||_36.roadmMode==="N-FIXED"||_36.roadmMode==="DUAL-CLIENT"),onChange:dojo.hitch(_36.steerableAddRadio,_36.radioOnChange,_36)});
var _3b=dojo.create("label",{"for":"steerableAddRadio","innerHTML":"Steerable Add"});
dojo.place(_36.steerableAddRadio.domNode,_36.steerableAddLi);
dojo.place(_3b,_36.steerableAddLi);
_36.steerableDropRadio=new dijit.form.RadioButton({id:"steerableDropRadio",value:"steerableDrop",name:"channelFunction",checked:(_36.roadmMode==="C-SELECT"),disabled:(_36.roadmMode==="DUAL-CLIENT"||_36.roadmMode==="C-SELECT"),onChange:dojo.hitch(_36.steerableDropRadio,_36.radioOnChange,_36)});
var _3c=dojo.create("label",{"for":"steerableDropRadio","innerHTML":"Steerable Drop"});
dojo.place(_36.steerableDropRadio.domNode,_36.steerableDropLi);
dojo.place(_3c,_36.steerableDropLi);
}
return _36.ulChannelFunction;
},radioOnChange:function(_3d){
var _3e=this;
if(_3e.get("value")){
_3d.channelFunction=_3e.get("value");
_3d.clearView();
dojo.hitch(_3d,_3d.getUnusedFromPoints)();
}
},onSelectFromChange:function(_3f){
if(_3f.selectToLi){
dojo.destroy(_3f.selectToLi);
_3f.selectTo.destroy();
}
var _3f=this;
_3f.FromAddress=_3f.selectFrom.get("value");
if(!_3f.FromAddress){
return;
}
dojo.forEach(_3f.widgetContainer,function(_40){
_40.destroy();
});
dojo.forEach(_3f.liContainer,function(_41){
dojo.empty(_41);
dojo.destroy(_41);
});
_3f.liContainer=[];
_3f.widgetContainer=[];
if(_3f.aidGroup==="AIDNAME_CH+AIDNAME_CRS_CH"){
_3f.aidGroup="AIDNAME_CH";
}
var _42=dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/addresses_config"),content:{originAddress:_3f.FromAddress,relation:"possibleToPoint",aidGroup:_3f.aidGroup},handleAs:"json",load:dojo.hitch(_3f,_3f.createToSelect)});
},createToSelect:function(_43){
var _44=this;
var _45=[];
var _46=(_44.equipmentType==="EROADM-DC")?_44.parentAddress.replace(/SHELF-(.+)/,"$1")+"-":_44.parentAddress.replace(/MOD-(.+)/,"$1")+"-";
var r;
if(_44.channelFunction){
if(_44.roadmTypeCDGC){
r=new RegExp(_46);
}else{
switch(_44.channelFunction){
case "passThru":
r=new RegExp(/-N/);
break;
case "drop":
case "addDrop":
r=new RegExp(_46+"C");
break;
case "add":
r=new RegExp(_46+"N");
break;
case "steerableAdd":
case "steerableDrop":
case "steerableAddDrop":
if(_44.roadmMode==="N-FIXED"||_44.roadmMode==="DUAL-CLIENT"){
r=new RegExp(/-C/);
}else{
r=new RegExp();
}
break;
}
}
dojo.forEach(_43.addresses,function(_47){
if(r.test(_47)){
if(_44.channelFunction==="steerableAddDrop"){
if(!new RegExp(_46).test(_47)){
_45.push(_47);
}
}else{
_45.push(_47);
}
}
});
}else{
_45=_43.addresses;
}
var _48=[];
dojo.forEach(_45,function(_49){
var _4a;
if(_44.equipmentType==="EROADM-DC"&&(_44.channelFunction==="addDrop"||_44.channelFunction==="drop")){
_4a=new dojo.Deferred();
_49=_49.replace(/^CH-/,"");
_48.push(_4a);
_4a.callback({"addresses":[_49]});
}else{
_4a=dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/addresses_config"),handleAs:"json",content:{originAddress:_49,relation:"parent"}});
_48.push(_4a);
}
});
var _4b=[];
webgui.wizard.linkedAid2label={};
var xhr=dojo.when(new dojo.DeferredList(_48),function(_4c){
dojo.forEach(_4c,function(r,idx){
if(!_45.length){
return;
}
var _4d=r[1].addresses[0];
var _4e=_45[idx];
var _4f=_4d.replace(/^OM-/,"");
_4b.push({value:_4e,valueDisp:_4f});
webgui.wizard.linkedAid2label[_4e]=_4f;
});
var _50=_44.createPortRow({id:"_wizard;linkedPort",parameters:_4b,label:"(B) Linked Port",onChange:dojo.hitch(_44,_44.onSelectToChange)});
_44.selectToLi=_50[0];
_44.selectTo=_50[1];
if(_4b.length===1){
_44.selectTo.set("disabled",true);
_44.selectTo.onChange();
}else{
if(!_4b.length){
_44.selectTo.set("disabled",true);
}
}
});
},onSelectToChange:function(){
var _51=this;
dojo.forEach(_51.widgetContainer,function(_52,idx){
_52.destroy();
});
dojo.forEach(_51.liContainer,function(_53,idx){
dojo.empty(_53);
dojo.destroy(_53);
});
_51.ToAddress=_51.selectTo.get("value");
_51.address1="CRS_CH-"+_51.FromAddress+","+_51.ToAddress;
_51.address2="CRS_CH-"+_51.ToAddress+","+_51.FromAddress;
var _54=dojo.xhrGet({url:webgui.utils.proxyUrl("/scripts/system_create_config?address="+_51.address1+"&"+webgui.xhrParam(_51.address1,"ALIAS")),handleAs:"json",load:dojo.hitch(_51,_51.createFinalParams)});
},createFinalParams:function(_55){
var _56=this;
_56.widgetContainer=[];
_56.hiddenParameters={};
var _57=false;
var _58=true;
var _59=dojo.clone(_55.parameters);
dojo.forEach(_59,function(_5a){
_58=(_58&&_5a.hasOwnProperty("value"));
var _5b;
if(_5a.keyword==="PATH-NODE"){
_5b=_56.createParamRow(_5a," (A &#8594; B)");
if(_56.channelFunction==="addDrop"||_56.channelFunction==="add"){
_5b.set("value",1);
}
_5b.onChange=dojo.hitch(_56,_56.onInputChange);
if(_56.directionValue==="2way"){
var _5c=dojo.clone(_5a);
_5c.address=_56.address2;
_56.NodePathReverseWidget=_56.createParamRow(_5c," (B &#8594; A)");
_56.NodePathReverseWidget.set("disabled",_57);
_56.NodePathReverseWidget.onChange=dojo.hitch(_56,_56.onInputChange);
}
}else{
if(_5a.keyword==="CONN"||_5a.keyword==="CONFIG__CRS"){
_56.hiddenParameters[_5a.keyword]=_5a;
}else{
_5b=_56.createParamRow(_5a);
_5b.onChange=dojo.hitch(_56,_56.onInputChange);
}
}
});
if(_58){
_56.onInputChange();
}
},onInputChange:function(){
var _5d=this;
var _5e=dojo.every(_5d.widgetContainer,function(_5f){
if(!_5f.validate()){
return false;
}
return true;
});
if(_5e){
_5d.submitButton.set("disabled",false);
}
},createParamRow:function(_60,_61){
var _61=(_61)?_61:"";
var _62=this;
var _63=dojo.create("li",{},_62.paneContainer.content);
var _64=dojo.create("div",{"class":"paramLabel"},_63);
var _65=dojo.create("div",{"class":"paramWidget"},_63);
var _66=dojo.create("label",{innerHTML:webgui.utils.parameterName(_60)+_61},_64);
var _67=webgui.utils.createDynamicWidget(_60);
_62.widgetContainer.push(_67);
dojo.place(_67.domNode,_65);
_62.liContainer.push(_63);
return _67;
},submitButtonClick:function(e){
var _68=this;
_68.submitButton.set("disabled",true);
var _69={};
var _6a={};
var _6b=false;
dojo.forEach(_68.widgetContainer,function(_6c){
var _6d=_6c.get("name");
var _6e=_6c.get("value");
if(_6d.indexOf(_68.address1)!==-1){
_69[_6d]=_6e;
if(_6d.indexOf("PATH-NODE")===-1){
var _6f=_6d.replace(_68.address1,_68.address2);
_6a[_6f]=_6e;
}
}else{
_6a[_6d]=_6e;
}
});
if(_68.hiddenParameters["CONFIG__CRS"]){
switch(_68.channelFunction){
case "passThru":
_69[webgui.utils.paramId(_68.address1,"CONFIG__CRS")]="PASS";
_6a[webgui.utils.paramId(_68.address2,"CONFIG__CRS")]="PASS";
break;
case "addDrop":
if(/(-C)/i.test(_68.selectFrom.get("value"))){
_69[webgui.utils.paramId(_68.address1,"CONFIG__CRS")]=(_68.roadmModeCDGC==="C-SELECT")?"DROP":"ADD";
_6a[webgui.utils.paramId(_68.address2,"CONFIG__CRS")]=(_68.roadmModeCDGC==="C-SELECT")?"ADD":"DROP";
}else{
if(/(-N)/i.test(_68.selectFrom.get("value"))){
_69[webgui.utils.paramId(_68.address1,"CONFIG__CRS")]=(_68.roadmModeCDGC==="C-SELECT")?"ADD":"DROP";
_6a[webgui.utils.paramId(_68.address2,"CONFIG__CRS")]=(_68.roadmModeCDGC==="C-SELECT")?"DROP":"ADD";
}
}
break;
case "add":
_69[webgui.utils.paramId(_68.address1,"CONFIG__CRS")]="ADD";
break;
case "drop":
_69[webgui.utils.paramId(_68.address1,"CONFIG__CRS")]="DROP";
break;
}
}
if(_68.hiddenParameters["CONN"]){
if(_68.directionValue==="1way"){
_6b=true;
_69[webgui.utils.paramId(_68.address1,"CONN")]="UNI";
}else{
if(_68.directionValue==="2way"){
_69[webgui.utils.paramId(_68.address1,"CONN")]="BI";
_6a[webgui.utils.paramId(_68.address2,"CONN")]="BI";
}
}
}
_69["address"]=_68.address1;
_6a["address"]=_68.address2;
var _70=dojo.xhrPost({url:webgui.utils.proxyUrl("/scripts/system_create_config"),content:_69,handleAs:"json"});
var _71;
if(_6b){
_71=new dojo.Deferred();
_71.callback({});
}else{
_71=dojo.xhrPost({url:webgui.utils.proxyUrl("/scripts/system_create_config"),content:_6a,handleAs:"json"});
}
var dl=[];
dl.push(_70);
dl.push(_71);
var xhr=dojo.when(new dojo.DeferredList(dl),function(_72){
if(_72[0][1].error||(_72[1]&&_72[1][1].error)){
var _73;
if((_72[0][1].error&&_72[0][1].error==="EXISTENT_ADDRESS")||(_72[1][1].error&&_72[1][1].error==="EXISTENT_ADDRESS")){
_73="One of Connections was not created because it already exists!";
}else{
_73="Cross Connection not created!";
}
webgui.utils.msg.error(_73,{container:_68.wizardDialog});
}else{
webgui.utils.msg.message("Cross Connection created successfully");
}
_68.wizardDialog.hide();
dojo.publish("/reload/config/openPanes");
});
}});

