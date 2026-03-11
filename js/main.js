(function(){
'use strict';
var burger=document.getElementById('burger-btn');
var nav=document.getElementById('nav');
if(burger&&nav){burger.addEventListener('click',function(){nav.classList.toggle('is-open');});}
var form=document.getElementById('request-form');
if(form){form.addEventListener('submit',function(e){e.preventDefault();return false;});}
})();