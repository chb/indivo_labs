//steal/js labs/scripts/compress.js

load("steal/rhino/steal.js");
steal('//steal/compress/compress',function(){
	steal.compress('labs/labs.html',{to: 'labs'})
})