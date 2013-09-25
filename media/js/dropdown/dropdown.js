var timeout         = 500;
var closetimer      = 0;
var ddmenuitem      = 0;

function topmenu_dropdown_open()
{   topmenu_dropdown_canceltimer();
    topmenu_dropdown_close();
    ddmenuitem = $(this).find('ul').eq(0).css('visibility', 'visible');}

function topmenu_dropdown_close()
{   if(ddmenuitem) ddmenuitem.css('visibility', 'hidden');}

function topmenu_dropdown_timer()
{   closetimer = window.setTimeout(topmenu_dropdown_close, timeout);}

function topmenu_dropdown_canceltimer()
{   if(closetimer)
    {   window.clearTimeout(closetimer);
        closetimer = null;}}

$(document).ready(function()
{   $('#topmenu_dropdown > li').bind('mouseover', topmenu_dropdown_open);
    $('#topmenu_dropdown > li').bind('mouseout',  topmenu_dropdown_timer);});

document.onclick = topmenu_dropdown_close;

