objects = document.getElementsByClassName('CatWrapping');
explorefield = document.getElementById('explorefield');
let leftbuffer = 0;
let defaultleft = new Array();
let defaulttop = new Array();
let moved = new Array();

for (let i = 0; i < objects.length; ++i){
    moved[i] = false;
    objects[i].addEventListener('click', function()
    {
        EllipseInner = $('#'+objects[i].id).children('EllipseInner')[0];
        EllipseContext = EllipseInner.getContext('2d');
        if(moved[i]){
            EllipseContext.fillstyle = 'rgba(51,51,51,1)';
        }else{
            EllipseContext.fillstyle = 'rgba(0,255,176,1)';
        }
        moved[i] = !moved[i];
    })
}

ObjReset = document.getElementsByClassName('reset');
ObjReset[0].addEventListener('click', function()
{   
    for (let i = 0; i < objects.length; ++i){
        if(moved[i]){
            anime({
                targets: '#'+objects[i].id,
                duration: 500,
                easing: 'linear',
                left: defaultleft[i]-window.pageXOffset-explorefield.getBoundingClientRect().left,
                top: defaulttop[i]-window.pageYOffset-explorefield.getBoundingClientRect().top
            })
            moved[i] = false;
        }
    }
    leftbuffer = 0;
})
