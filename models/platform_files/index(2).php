savedStats=[];function saveStat(url,area,id,type){if(savedStats[id]){return true;}else{$.post(urlPath(url),{sitearea:area,siteareaid:id,type:type});}
savedStats[id]=true;}
function measureWidth(selector){var item=$(selector).eq(0);var pos=item.css("position");item.css("position","absolute");var width=item.width();item.css("position",pos);return(width);}
function measureHeight(selector){var item=$(selector).eq(0);var pos=item.css("position");item.css("position","absolute");var height=item.height();item.css("position",pos);return(height);}
function urlPath(urlstr){if(urlstr.indexOf("://")>=0){urlstr=urlstr.substring(urlstr.indexOf("://")+3);urlstr=urlstr.indexOf("/")?urlstr.substring(urlstr.indexOf("/")):"/";}
return urlstr;}
function saveUpdate(element,action,callback,confirmtxt,microtimeout){var doupdate=true,datastr="";if(confirmtxt){if(confirmtxt.match(/your reason|following reason/)){str=prompt(confirmtxt);if(str){datastr="&arcmsg="+encodeURI(str);}else if(str!=""){doupdate=false;}}else{doupdate=confirm(confirmtxt);}}
if(doupdate){if(element.hasClass('ajaxicon')){element.html('Please Wait...');}else{text=element.html();if(element.addClass('ajaxicon').attr('href').indexOf('?')>0){var arguments=element.attr('href').split('?');var urlstr=arguments[0];var datastr=datastr+"&"+arguments[1].replace(/#.*$/,"");}else{var urlstr=element.attr('href');}
$.ajax({type:'POST',url:urlPath(urlstr),timeout:(microtimeout?microtimeout:60000),dataType:'json',data:"ajax=t"+datastr,error:function(response,error,exception){element.removeClass('ajaxicon').html(text);$.achtung({message:'An error has occurred updating the item requested. Please try again shortly.',className:'achtungFail',timeout:5});},success:function(response){element.removeClass('ajaxicon').html(text);if(response['error']){$.achtung({message:response['text'],className:'achtungFail',timeout:typeof response["timeout"]=="number"&&response["timeout"]>0?response["timeout"]:10});}else if(response['text']){$.achtung({message:response['text'],className:'achtungSuccess',timeout:typeof response["timeout"]=="number"&&response["timeout"]>0?response["timeout"]:10});}
if(response['labels']){for(i in response['labels']){element.parent().find("."+i+"icon").attr("title",response['labels'][i]).html(response['labels'][i]).change();}}
if(response['count']){for(i in response['count']){if(!isNaN(parseInt(response["count"][i]))){$("."+i+"count").text(response['count'][i]);}}}
if(response['hidetooltip']){if(element.closest('.sidecolumn').length>0){$('.headernormalbox .errortooltip').removeClass('errortooltip').text('');}else{element.closest('.normalbox').find('.errortooltip').removeClass('errortooltip').text('');}}
if(callback){callback(element,response);}}});}}};$.fn.toggleDescription=function(field,hidesummary){summary=$(this).text().trim();if(summary.substr(summary.length-1).match(/^[a-z0-9]$/i)){$(this).html(summary+".");}
$(this).append(' <a href="#" id="toggle'+field+'description">Read more...</a>');$("#toggle"+field+"description").click(function(){$(this).remove();$("#"+field+"description img,#"+field+"description iframe").each(function(){if($(this).data("src")){$(this).attr("src",$(this).data("src")).removeData("src").removeAttr("data-src");}});$("#"+field+"description").slideDown();if(hidesummary){$("#"+field+"summary").remove();}
return false;});};$.fn.saveUpdate=function(action,callback,confirmtxt,microtimeout){$(this).click(function(){saveUpdate($(this),action,callback,confirmtxt,microtimeout);return false;});};;
/*!
 * JavaScript Cookie v2.2.0
 * https://github.com/js-cookie/js-cookie
 *
 * Copyright 2006, 2015 Klaus Hartl & Fagner Brack
 * Released under the MIT license
 */
;(function(factory){var registeredInModuleLoader=false;if(typeof define==='function'&&define.amd){define(factory);registeredInModuleLoader=true;}
if(typeof exports==='object'){module.exports=factory();registeredInModuleLoader=true;}
if(!registeredInModuleLoader){var OldCookies=window.Cookies;var api=window.Cookies=factory();api.noConflict=function(){window.Cookies=OldCookies;return api;};}}(function(){function extend(){var i=0;var result={};for(;i<arguments.length;i++){var attributes=arguments[i];for(var key in attributes){result[key]=attributes[key];}}
return result;}
function init(converter){function api(key,value,attributes){var result;if(typeof document==='undefined'){return;}
if(arguments.length>1){attributes=extend({path:'/'},api.defaults,attributes);if(typeof attributes.expires==='number'){var expires=new Date();expires.setMilliseconds(expires.getMilliseconds()+attributes.expires*864e+5);attributes.expires=expires;}
attributes.expires=attributes.expires?attributes.expires.toUTCString():'';try{result=JSON.stringify(value);if(/^[\{\[]/.test(result)){value=result;}}catch(e){}
if(!converter.write){value=encodeURIComponent(String(value)).replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g,decodeURIComponent);}else{value=converter.write(value,key);}
key=encodeURIComponent(String(key));key=key.replace(/%(23|24|26|2B|5E|60|7C)/g,decodeURIComponent);key=key.replace(/[\(\)]/g,escape);var stringifiedAttributes='';for(var attributeName in attributes){if(!attributes[attributeName]){continue;}
stringifiedAttributes+='; '+attributeName;if(attributes[attributeName]===true){continue;}
stringifiedAttributes+='='+attributes[attributeName];}
return(document.cookie=key+'='+value+stringifiedAttributes);}
if(!key){result={};}
var cookies=document.cookie?document.cookie.split('; '):[];var rdecode=/(%[0-9A-Z]{2})+/g;var i=0;for(;i<cookies.length;i++){var parts=cookies[i].split('=');var cookie=parts.slice(1).join('=');if(!this.json&&cookie.charAt(0)==='"'){cookie=cookie.slice(1,-1);}
try{var name=parts[0].replace(rdecode,decodeURIComponent);cookie=converter.read?converter.read(cookie,name):converter(cookie,name)||cookie.replace(rdecode,decodeURIComponent);if(this.json){try{cookie=JSON.parse(cookie);}catch(e){}}
if(key===name){result=cookie;break;}
if(!key){result[name]=cookie;}}catch(e){}}
return result;}
api.set=api;api.get=function(key){return api.call(api,key);};api.getJSON=function(){return api.apply({json:true},[].slice.call(arguments));};api.defaults={};api.remove=function(key,attributes){api(key,'',extend(attributes,{expires:-1}));};api.withConverter=init;return api;}
return init(function(){});}));;
/*!
 jQuery ColorBox v1.4.2 - 2013-02-18
 (c) 2013 Jack Moore - jacklmoore.com/colorbox
 license: https://opensource.org/licenses/mit-license.php
*/
(function($,document,window){var
defaults={transition:"elastic",speed:300,width:false,initialWidth:"600",innerWidth:false,maxWidth:false,height:false,initialHeight:"450",innerHeight:false,maxHeight:false,scalePhotos:true,scrolling:true,inline:false,html:false,iframe:false,fastIframe:true,photo:false,href:false,title:false,rel:false,opacity:false,preloading:true,className:false,retinaImage:false,retinaUrl:false,retinaSuffix:'@2x.$1',current:"image {current} of {total}",previous:"previous",next:"next",close:"close",xhrError:"This content failed to load.",imgError:"This image failed to load.",open:false,returnFocus:true,reposition:true,loop:true,slideshow:false,slideshowAuto:true,slideshowSpeed:2500,slideshowStart:"start slideshow",slideshowStop:"stop slideshow",photoRegex:/\.(gif|png|jp(e|g|eg)|bmp|ico)((#|\?).*)?$/i,onOpen:false,onLoad:false,onComplete:false,onCleanup:false,onClosed:false,overlayClose:true,escKey:true,arrowKey:true,top:false,bottom:false,left:false,right:false,fixed:false,data:undefined},colorbox='colorbox',prefix='cbox',boxElement=prefix+'Element',event_open=prefix+'_open',event_load=prefix+'_load',event_complete=prefix+'_complete',event_cleanup=prefix+'_cleanup',event_closed=prefix+'_closed',event_purge=prefix+'_purge',isIE=!$.support.leadingWhitespace,isIE6=isIE&&!window.XMLHttpRequest,event_ie6=prefix+'_IE6',$overlay,$box,$wrap,$content,$topBorder,$leftBorder,$rightBorder,$bottomBorder,$related,$window,$loaded,$loadingBay,$loadingOverlay,$title,$current,$slideshow,$next,$prev,$close,$groupControls,$events=$({}),settings,interfaceHeight,interfaceWidth,loadedHeight,loadedWidth,element,index,photo,open,active,closing,loadingTimer,publicMethod,div="div",className,init;function $tag(tag,id,css){var element=document.createElement(tag);if(id){element.id=prefix+id;}
if(css){element.style.cssText=css;}
return $(element);}
function getIndex(increment){var
max=$related.length,newIndex=(index+increment)%max;return(newIndex<0)?max+newIndex:newIndex;}
function setSize(size,dimension){return Math.round((/%/.test(size)?((dimension==='x'?$window.width():$window.height())/100):1)*parseInt(size,10));}
function isImage(url){return settings.photo||settings.photoRegex.test(url);}
function retinaUrl(url){return settings.retinaUrl&&window.devicePixelRatio>1?url.replace(settings.photoRegex,settings.retinaSuffix):url;}
function trapFocus(e){if('contains'in $box[0]&&!$box[0].contains(e.target)){e.stopPropagation();$box.focus();}}
function makeSettings(){var i,data=$.data(element,colorbox);if(data==null){settings=$.extend({},defaults);if(console&&console.log){console.log('Error: cboxElement missing settings object');}}else{settings=$.extend({},data);}
for(i in settings){if($.isFunction(settings[i])&&i.slice(0,2)!=='on'){settings[i]=settings[i].call(element);}}
settings.rel=settings.rel||element.rel||$(element).data('rel')||'nofollow';settings.href=settings.href||$(element).attr('href');settings.title=settings.title||element.title;if(settings.rel.indexOf('=')!=-1){settingsarray=settings.rel.split(';');for(x in settingsarray){settingstemp=settingsarray[x].split('=');settings[settingstemp[0]]=settingstemp[1];}
settings.rel='nofollow';}
if(typeof settings.href==="string"){settings.href=$.trim(settings.href);}}
function trigger(event,callback){$(document).trigger(event);$events.trigger(event);if($.isFunction(callback)){callback.call(element);}}
function slideshow(){var
timeOut,className=prefix+"Slideshow_",click="click."+prefix,clear,set,start,stop;if(settings.slideshow&&$related[1]){clear=function(){clearTimeout(timeOut);};set=function(){if(settings.loop||$related[index+1]){timeOut=setTimeout(publicMethod.next,settings.slideshowSpeed);}};start=function(){$slideshow.html(settings.slideshowStop).unbind(click).one(click,stop);$events.bind(event_complete,set).bind(event_load,clear).bind(event_cleanup,stop);$box.removeClass(className+"off").addClass(className+"on");};stop=function(){clear();$events.unbind(event_complete,set).unbind(event_load,clear).unbind(event_cleanup,stop);$slideshow.html(settings.slideshowStart).unbind(click).one(click,function(){publicMethod.next();start();});$box.removeClass(className+"on").addClass(className+"off");};if(settings.slideshowAuto){start();}else{stop();}}else{$box.removeClass(className+"off "+className+"on");}}
function launch(target){if(!closing){element=target;makeSettings();$related=$(element);index=0;if(settings.rel!=='nofollow'){$related=$('.'+boxElement).filter(function(){var data=$.data(this,colorbox),relRelated;if(data){relRelated=$(this).data('rel')||data.rel||this.rel;}
return(relRelated===settings.rel);});index=$related.index(element);if(index===-1){$related=$related.add(element);index=$related.length-1;}}
$overlay.css({opacity:parseFloat(settings.opacity),cursor:settings.overlayClose?"pointer":"auto",visibility:'visible'}).show();if(!open){open=active=true;$box.css({visibility:'hidden',display:'block'});$loaded=$tag(div,'LoadedContent','width:0; height:0; overflow:hidden').appendTo($content);interfaceHeight=$topBorder.height()+$bottomBorder.height()+$content.outerHeight(true)-$content.height();interfaceWidth=$leftBorder.width()+$rightBorder.width()+$content.outerWidth(true)-$content.width();loadedHeight=$loaded.outerHeight(true);loadedWidth=$loaded.outerWidth(true);settings.w=setSize(settings.initialWidth,'x');settings.h=setSize(settings.initialHeight,'y');publicMethod.position();if(isIE6){$window.bind('resize.'+event_ie6+' scroll.'+event_ie6,function(){$overlay.css({width:$window.width(),height:$window.height(),top:$window.scrollTop(),left:$window.scrollLeft()});}).trigger('resize.'+event_ie6);}
slideshow();trigger(event_open,settings.onOpen);$groupControls.add($title).hide();$close.html(settings.close).show();$box.focus();if(document.addEventListener){document.addEventListener('focus',trapFocus,true);$events.one(event_closed,function(){document.removeEventListener('focus',trapFocus,true);});}
if(settings.returnFocus){$events.one(event_closed,function(){$(element).focus();});}}
publicMethod.load(true);}}
function appendHTML(){if(!$box&&document.body){init=false;$window=$(window);$box=$tag(div).attr({id:colorbox,'class':isIE?prefix+(isIE6?'IE6':'IE'):'',role:'dialog',tabindex:'-1'}).hide();$overlay=$tag(div,"Overlay",isIE6?'position:absolute':'').hide();$loadingOverlay=$tag(div,"LoadingOverlay").add($tag(div,"LoadingGraphic"));$wrap=$tag(div,"Wrapper");$content=$tag(div,"Content").append($title=$tag(div,"Title"),$current=$tag(div,"Current"),$prev=$tag('button',"Previous"),$next=$tag('button',"Next"),$slideshow=$tag('button',"Slideshow"),$loadingOverlay,$close=$tag('button',"Close"));$wrap.append($tag(div).append($tag(div,"TopLeft"),$topBorder=$tag(div,"TopCenter"),$tag(div,"TopRight")),$tag(div,false,'clear:left').append($leftBorder=$tag(div,"MiddleLeft"),$content,$rightBorder=$tag(div,"MiddleRight")),$tag(div,false,'clear:left').append($tag(div,"BottomLeft"),$bottomBorder=$tag(div,"BottomCenter"),$tag(div,"BottomRight"))).find('div div').css({'float':'left'});$loadingBay=$tag(div,false,'position:absolute; width:9999px; visibility:hidden; display:none');$groupControls=$next.add($prev).add($current).add($slideshow);$(document.body).append($overlay,$box.append($wrap,$loadingBay));}}
function addBindings(){function clickHandler(e){if(!(e.which>1||e.shiftKey||e.altKey||e.metaKey)){e.preventDefault();launch(this);}}
if($box){if(!init){init=true;$next.click(function(){publicMethod.next();});$prev.click(function(){publicMethod.prev();});$close.click(function(){publicMethod.close();});$overlay.click(function(){if(settings.overlayClose){publicMethod.close();}});$(document).bind('keydown.'+prefix,function(e){var key=e.keyCode;if(open&&settings.escKey&&key===27){e.preventDefault();publicMethod.close();}
if(open&&settings.arrowKey&&$related[1]&&!e.altKey){if(key===37){e.preventDefault();$prev.click();}else if(key===39){e.preventDefault();$next.click();}}});$(document).on('click.'+prefix,'.'+boxElement,clickHandler);}
return true;}
return false;}
if($.colorbox){return;}
$(appendHTML);publicMethod=$.fn[colorbox]=$[colorbox]=function(options,callback){var $this=this;options=options||{};appendHTML();if(addBindings()){if($.isFunction($this)){$this=$('<a/>');options.open=true;}else if(!$this[0]){return $this;}
if(callback){options.onComplete=callback;}
$this.each(function(){$.data(this,colorbox,$.extend({},$.data(this,colorbox)||defaults,options));}).addClass(boxElement);if(($.isFunction(options.open)&&options.open.call($this))||options.open){launch($this[0]);}}
return $this;};publicMethod.position=function(speed,loadedCallback){var
css,top=0,left=0,offset=$box.offset(),scrollTop,scrollLeft;$window.unbind('resize.'+prefix);$box.css({top:-9e4,left:-9e4});scrollTop=$window.scrollTop();scrollLeft=$window.scrollLeft();if(settings.fixed&&!isIE6){offset.top-=scrollTop;offset.left-=scrollLeft;$box.css({position:'fixed'});}else{top=scrollTop;left=scrollLeft;$box.css({position:'absolute'});}
if(settings.right!==false){left+=Math.max($window.width()-settings.w-loadedWidth-interfaceWidth-setSize(settings.right,'x'),0);}else if(settings.left!==false){left+=setSize(settings.left,'x');}else{left+=Math.round(Math.max($window.width()-settings.w-loadedWidth-interfaceWidth,0)/2);}
if(settings.bottom!==false){top+=Math.max($window.height()-settings.h-loadedHeight-interfaceHeight-setSize(settings.bottom,'y'),0);}else if(settings.top!==false){top+=setSize(settings.top,'y');}else{top+=Math.round(Math.max($window.height()-settings.h-loadedHeight-interfaceHeight,0)/2);}
$box.css({top:offset.top,left:offset.left,visibility:'visible'});speed=($box.width()===settings.w+loadedWidth&&$box.height()===settings.h+loadedHeight)?0:speed||0;$wrap[0].style.width=$wrap[0].style.height="9999px";function modalDimensions(that){$topBorder[0].style.width=$bottomBorder[0].style.width=$content[0].style.width=(parseInt(that.style.width,10)-interfaceWidth)+'px';$content[0].style.height=$leftBorder[0].style.height=$rightBorder[0].style.height=(parseInt(that.style.height,10)-interfaceHeight)+'px';}
css={width:settings.w+loadedWidth+interfaceWidth,height:settings.h+loadedHeight+interfaceHeight,top:top,left:left};if(speed===0){$box.css(css);}
$box.dequeue().animate(css,{duration:speed,complete:function(){modalDimensions(this);active=false;$wrap[0].style.width=(settings.w+loadedWidth+interfaceWidth)+"px";$wrap[0].style.height=(settings.h+loadedHeight+interfaceHeight)+"px";if(settings.reposition){setTimeout(function(){$window.bind('resize.'+prefix,publicMethod.position);},1);}
if(loadedCallback){loadedCallback();}},step:function(){modalDimensions(this);}});};publicMethod.resize=function(options){if(open){options=options||{};if(options.width){settings.w=setSize(options.width,'x')-loadedWidth-interfaceWidth;}
if(options.innerWidth){settings.w=setSize(options.innerWidth,'x');}
$loaded.css({width:settings.w});if(options.height){settings.h=setSize(options.height,'y')-loadedHeight-interfaceHeight;}
if(options.innerHeight){settings.h=setSize(options.innerHeight,'y');}
if(!options.innerHeight&&!options.height){$loaded.css({height:"auto"});settings.h=$loaded.height();}
$loaded.css({height:settings.h});publicMethod.position(settings.transition==="none"?0:settings.speed);}};publicMethod.prep=function(object){if(!open){return;}
var callback,speed=settings.transition==="none"?0:settings.speed;$loaded.empty().remove();$loaded=$tag(div,'LoadedContent').append(object);function getWidth(){settings.w=settings.w||$loaded.width();settings.w=settings.mw&&settings.mw<settings.w?settings.mw:settings.w;return settings.w;}
function getHeight(){settings.h=settings.h||$loaded.height();settings.h=settings.mh&&settings.mh<settings.h?settings.mh:settings.h;return settings.h;}
$loaded.hide().appendTo($loadingBay.show()).css({width:getWidth(),overflow:settings.scrolling?'auto':'hidden'}).css({height:getHeight()}).prependTo($content);$loadingBay.hide();$(photo).css({'float':'none'});callback=function(){var total=$related.length,iframe,frameBorder='frameBorder',allowTransparency='allowTransparency',complete;if(!open){return;}
function removeFilter(){if(isIE){$box[0].style.removeAttribute('filter');}}
complete=function(){clearTimeout(loadingTimer);$loadingOverlay.hide();trigger(event_complete,settings.onComplete);};if(isIE){if(photo){$loaded.fadeIn(100);}}
$title.html(settings.title).add($loaded).show();if(total>1){if(typeof settings.current==="string"){$current.html(settings.current.replace('{current}',index+1).replace('{total}',total)).show();}
$next[(settings.loop||index<total-1)?"show":"hide"]().html(settings.next);$prev[(settings.loop||index)?"show":"hide"]().html(settings.previous);if(settings.slideshow){$slideshow.show();}
if(settings.preloading){$.each([getIndex(-1),getIndex(1)],function(){var src,img,i=$related[this],data=$.data(i,colorbox);if(data&&data.href){src=data.href;if($.isFunction(src)){src=src.call(i);}}else{src=$(i).attr('href');}
if(src&&(isImage(src)||data.photo)){img=new Image();img.src=src;}});}}else{$groupControls.hide();}
if(settings.iframe){iframe=$tag('iframe')[0];if(frameBorder in iframe){iframe[frameBorder]=0;}
if(allowTransparency in iframe){iframe[allowTransparency]="true";}
if(!settings.scrolling){iframe.scrolling="no";}
$(iframe).attr({src:settings.href,name:(new Date()).getTime(),'class':prefix+'Iframe',allowFullScreen:true,webkitAllowFullScreen:true,mozallowfullscreen:true}).one('load',complete).appendTo($loaded);$events.one(event_purge,function(){iframe.src="//about:blank";});if(settings.fastIframe){$(iframe).trigger('load');}}else{complete();}
if(settings.transition==='fade'){$box.fadeTo(speed,1,removeFilter);}else{removeFilter();}};if(settings.transition==='fade'){$box.fadeTo(speed,0,function(){publicMethod.position(0,callback);});}else{publicMethod.position(speed,callback);}};publicMethod.load=function(launched){var href,setResize,prep=publicMethod.prep,$inline;active=true;photo=false;element=$related[index];if(!launched){makeSettings();}
if(className){$box.add($overlay).removeClass(className);}
if(settings.className){$box.add($overlay).addClass(settings.className);}
className=settings.className;trigger(event_purge);trigger(event_load,settings.onLoad);settings.h=settings.height?setSize(settings.height,'y')-loadedHeight-interfaceHeight:settings.innerHeight&&setSize(settings.innerHeight,'y');settings.w=settings.width?setSize(settings.width,'x')-loadedWidth-interfaceWidth:settings.innerWidth&&setSize(settings.innerWidth,'x');settings.mw=settings.w;settings.mh=settings.h;if(settings.maxWidth){settings.mw=setSize(settings.maxWidth,'x')-loadedWidth-interfaceWidth;settings.mw=settings.w&&settings.w<settings.mw?settings.w:settings.mw;}
if(settings.maxHeight){settings.mh=setSize(settings.maxHeight,'y')-loadedHeight-interfaceHeight;settings.mh=settings.h&&settings.h<settings.mh?settings.h:settings.mh;}
href=settings.href;loadingTimer=setTimeout(function(){$loadingOverlay.show();},100);if(settings.inline){$inline=$tag(div).hide().insertBefore($(href)[0]);$events.one(event_purge,function(){$inline.replaceWith($loaded.children());});prep($(href));}else if(settings.iframe){prep(" ");}else if(settings.html){prep(settings.html);}else if(isImage(href)){href=retinaUrl(href);$(photo=new Image()).addClass(prefix+'Photo').bind('error',function(){settings.title=false;prep($tag(div,'Error').html(settings.imgError));}).one('load',function(){var percent;if(settings.retinaImage&&window.devicePixelRatio>1){photo.height=photo.height/window.devicePixelRatio;photo.width=photo.width/window.devicePixelRatio;}
if(settings.scalePhotos){setResize=function(){photo.height-=photo.height*percent;photo.width-=photo.width*percent;};if(settings.mw&&photo.width>settings.mw){percent=(photo.width-settings.mw)/photo.width;setResize();}
if(settings.mh&&photo.height>settings.mh){percent=(photo.height-settings.mh)/photo.height;setResize();}}
if(settings.h){photo.style.marginTop=Math.max(settings.mh-photo.height,0)/2+'px';}
if($related[1]&&(settings.loop||$related[index+1])){photo.style.cursor='pointer';photo.onclick=function(){publicMethod.next();};}
if(isIE){photo.style.msInterpolationMode='bicubic';}
setTimeout(function(){prep(photo);},1);});setTimeout(function(){photo.src=href;},1);}else if(href){$loadingBay.load(href,settings.data,function(data,status){prep(status==='error'?$tag(div,'Error').html(settings.xhrError):$(this).contents());});}};publicMethod.next=function(){if(!active&&$related[1]&&(settings.loop||$related[index+1])){index=getIndex(1);publicMethod.load();}};publicMethod.prev=function(){if(!active&&$related[1]&&(settings.loop||index)){index=getIndex(-1);publicMethod.load();}};publicMethod.close=function(){if(open&&!closing){closing=true;open=false;trigger(event_cleanup,settings.onCleanup);$window.unbind('.'+prefix+' .'+event_ie6);$overlay.fadeTo(200,0);$box.stop().fadeTo(300,0,function(){$box.add($overlay).css({'opacity':'',cursor:''}).hide();trigger(event_purge);$loaded.empty().remove();setTimeout(function(){closing=false;trigger(event_closed,settings.onClosed);},1);});}};publicMethod.remove=function(){$([]).add($box).add($overlay).remove();$box=null;$('.'+boxElement).removeData(colorbox).removeClass(boxElement);$(document).unbind('click.'+prefix);};publicMethod.element=function(){return $(element);};publicMethod.settings=defaults;}(jQuery,document,window));;(function($){$.fn.achtung=function(options)
{var isMethodCall=(typeof options==='string'),args=Array.prototype.slice.call(arguments,0),name='achtung';return this.each(function(){var instance=$.data(this,name);if(isMethodCall&&options.substring(0,1)==='_'){return this;}
(!instance&&!isMethodCall&&$.data(this,name,new $.achtung(this))._init(args));(instance&&isMethodCall&&$.isFunction(instance[options])&&instance[options].apply(instance,args.slice(1)));});};$.achtung=function(element)
{var args=Array.prototype.slice.call(arguments,0),$el;if(!element||!element.nodeType){$el=$('<div />');return $el.achtung.apply($el,args);}
this.$container=$(element);};$.extend($.achtung,{version:'0.3.0',$overlay:false,defaults:{timeout:10,disableClose:false,icon:false,className:'',animateClassSwitch:false,showEffects:{'opacity':'toggle','height':'toggle'},hideEffects:{'opacity':'toggle','height':'toggle'},showEffectDuration:500,hideEffectDuration:700}});$.extend($.achtung.prototype,{$container:false,closeTimer:false,options:{},_init:function(args)
{var o,self=this;args=$.isArray(args)?args:[];args.unshift($.achtung.defaults);args.unshift({});o=this.options=$.extend.apply($,args);if(!$.achtung.$overlay){$.achtung.$overlay=$('<div id="achtung-overlay"></div>').appendTo(document.body);}
if(!o.disableClose){this.$container.click(function(){self.close();});}
this.changeIcon(o.icon,true);if(o.message){this.$container.append($('<span class="achtung-message">'+o.message+'</span>'));}
(o.className&&this.$container.addClass(o.className));(o.css&&this.$container.css(o.css));this.$container.addClass('achtung').appendTo($.achtung.$overlay);if(o.showEffects){this.$container.animate(o.showEffects,o.showEffectDuration);}else{this.$container.show();}
if(o.timeout>0){this.timeout(o.timeout);}},timeout:function(timeout)
{var self=this;if(this.closeTimer){clearTimeout(this.closeTimer);}
this.closeTimer=setTimeout(function(){self.close();},timeout*1000);this.options.timeout=timeout;},changeClass:function(newClass)
{var self=this;if(this.options.className===newClass){return;}
this.$container.queue(function(){if(!self.options.animateClassSwitch||/webkit/.test(navigator.userAgent.toLowerCase())||!$.isFunction($.fn.switchClass)){self.$container.removeClass(self.options.className);self.$container.addClass(newClass);}else{self.$container.switchClass(self.options.className,newClass,500);}
self.options.className=newClass;self.$container.dequeue();});},changeIcon:function(newIcon,force)
{var self=this;if((force!==true||newIcon===false)&&this.options.icon===newIcon){return;}
if(force||this.options.icon===false){this.$container.prepend($('<span class="achtung-message-icon ui-icon '+newIcon+'" />'));this.options.icon=newIcon;return;}else if(newIcon===false){this.$container.find('.achtung-message-icon').remove();this.options.icon=false;return;}
this.$container.queue(function(){var $span=$('.achtung-message-icon',self.$container);if(!self.options.animateClassSwitch||/webkit/.test(navigator.userAgent.toLowerCase())||!$.isFunction($.fn.switchClass)){$span.removeClass(self.options.icon);$span.addClass(newIcon);}else{$span.switchClass(self.options.icon,newIcon,500);}
self.options.icon=newIcon;self.$container.dequeue();});},changeMessage:function(newMessage)
{this.$container.queue(function(){$('.achtung-message',$(this)).html(newMessage);$(this).dequeue();});},update:function(options)
{(options.className&&this.changeClass(options.className));(options.css&&this.$container.css(options.css));(typeof(options.icon)!=='undefined'&&this.changeIcon(options.icon));(options.message&&this.changeMessage(options.message));(options.timeout&&this.timeout(options.timeout));},close:function()
{var o=this.options,$container=this.$container;if(o.hideEffects){this.$container.animate(o.hideEffects,o.hideEffectDuration);}else{this.$container.hide();}
$container.queue(function(){$container.removeData('achtung');$container.remove();if($.achtung.$overlay&&$.achtung.$overlay.is(':empty')){$.achtung.$overlay.remove();$.achtung.$overlay=false;}
$container.dequeue();});}});})(jQuery);;(function($){$.suggestClick=function(input,options){var $input=$(input).attr("autocomplete","off");var $results=$(document.createElement("ul"));var performing=false;var timeout=false;var prevLength=0;var cache=[];var cachedb=[];$results.addClass(options.resultsClass).appendTo(options.positionIn?options.positionIn:'body');$(window).resize(resetPosition);$input.focus(function(){resetPosition();suggest();});$input.blur(function(){setTimeout(function(){$results.hide()},200);});$input.keyup(processKey);function resetPosition(){if($(this).attr("autocomplete")){$input=$(this).attr("autocomplete","off");}
if(!options.noPosition){if(!options.positionIn&&options.positionElement){var top=$(options.positionElement).offset().top+$(options.positionElement).outerHeight();var left=$(options.positionElement).offset().left;var width=$(options.positionElement).width();}else if(!options.positionIn){var top=$input.offset().top+input.offsetHeight;var left=$input.offset().left;var width=$input.width()+4;}
$results.css({top:top+'px',left:left+'px',width:width+'px'});}}
function processKey(e){if((/27$|38$|40$/.test(e.keyCode)&&$results.is(':visible'))||(/^13$|^9$/.test(e.keyCode)&&getCurrentResult())){if(e.preventDefault){e.preventDefault();}
if(e.stopPropagation){e.stopPropagation();}
e.cancelBubble=true;e.returnValue=false;switch(e.keyCode){case 38:prevResult();break;case 40:nextResult();break;case 9:case 13:selectCurrentResult();break;case 27:$results.hide();break;}}else{setTimeout(doSuggest,options.delay);}}
function doSuggest(){if($input.val().length!=prevLength){if(performing){setTimeout(doSuggest,options.delay);}else{if(timeout){clearTimeout(timeout);}
var q=$.trim($input.val()).toLowerCase();var delay=cache[q]==undefined?0:(options.delay*5);prevLength=$input.val().length;if(delay){timeout=setTimeout(suggest,delay);}else{suggest();}}}}
function suggest(){var q=$.trim($input.val()).toLowerCase();if(q.length>=options.minchars){cached=checkCache(q);if(cached){displayItems(cached);}else{performing=true;$.get(options.source,{q:q,l:options.limit},function(txt){$results.hide();var items=parseTxt(txt);displayItems(items);addToCache(q,items);performing=false;});}}else{$results.hide();}}
function checkCache(q){if(cache[q]==undefined&&q.length>=options.minchars){var search='';var attempted=false;for(x in q){search+=q[x];if(search.length>=options.minchars&&cachedb[search]!=undefined&&cache[search]!=undefined&&!cache[search].length){attempted=true;return[];}}
if(attempted){return[];}else{return false;}}else if(cache[q]==undefined){return false;}else{return cache[q];}}
function addToCache(q,items){if(cache[q]==undefined){cache[q]=items;cachedb[q]=true;}}
function displayItems(items){if(!items){return;}
if(!items.length){$results.hide();return;}
var html='';for(i in items){html+='<li>'+items[i]+'</li>';}
$results.html(html).show();$results.children('li').mouseover(function(){$results.children('li').removeClass(options.selectClass).removeClass(options.selectClass+"next");$(this).addClass(options.selectClass).next().addClass(options.selectClass+"next");});}
function parseTxt(txt){var items=[];var tokens=txt.split(options.delimiter);for(var i=0;i<tokens.length;i++){var token=$.trim(tokens[i]);if(token){items[items.length]=token;}}
return items;}
function getCurrentResult(){if(!$results.is(':visible')){return false;}
var $currentResult=$results.children('li.'+options.selectClass);if(!$currentResult.length){$currentResult=false;}
return $currentResult;}
function selectCurrentResult(){$currentResult=getCurrentResult();if($currentResult){location.href=$currentResult.find('a').attr('href');}}
function nextResult(){$currentResult=getCurrentResult();$results.children('li').removeClass(options.selectClass).removeClass(options.selectClass+"next");if($currentResult){var applyto=$currentResult.next();}else{var applyto=$results.children('li:first-child');}
applyto.addClass(options.selectClass).next().addClass(options.selectClass+"next");}
function prevResult(){$currentResult=getCurrentResult();$results.children('li').removeClass(options.selectClass).removeClass(options.selectClass+"next");if($currentResult){var applyto=$currentResult.addClass(options.selectClass+"next").prev();}else{var applyto=$results.children('li:last-child');}
applyto.addClass(options.selectClass);}}
$.fn.suggestClick=function(source,options){if(!source){return;}
options=options||{};options.source=source;options.delay=options.delay||10;options.limit=options.limit||10;options.resultsClass=options.resultsClass||'suggest_results';options.selectClass=options.selectClass||'suggest_over';options.noPosition=options.noPosition||false;options.positionElement=options.positionElement||false;options.positionIn=options.positionIn||false;options.minchars=options.minchars||2;options.delimiter=options.delimiter||'\n';this.each(function(){new $.suggestClick(this,options);});return this;};})(jQuery);