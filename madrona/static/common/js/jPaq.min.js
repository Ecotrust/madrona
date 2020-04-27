/*
 jPaq - A fully customizable JavaScript/JScript library
 http://jpaq.org/

 Copyright (c) 2011 Christopher West
 Licensed under the MIT license.
 http://jpaq.org/license/

 Version: 1.0.6.08
 Revised: April 6, 2011
*/
(function(){jPaq={toString:function(){return"jPaq - A fully customizable JavaScript/JScript library created by Christopher West."}};Array.prototype.subtract=function(a){if(!(a instanceof Array))return[];for(var b,c=0,d=[],e=[];c<this.length;c++){for(b=0;b<a.length;b++)if(e[b]!=!0&&a[b]===this[c]){e[b]=!0;break}b==a.length&&d.push(this[c])}return d};Array.prototype.intersect=function(a){if(!(a instanceof Array))return[];return this.subtract(this.subtract(a))};Array.prototype.union=function(a){if(!(a instanceof
Array))return[];return this.concat(a.subtract(this))}})();
