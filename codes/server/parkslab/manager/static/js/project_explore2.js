objects = document.getElementsByClassName('CatWrapping');
explorefield = document.getElementById('explorefield');

for (let i = 0; i < objects.length; ++i){
    objects[i].addEventListener('click', function()
    {
        EllipseInner = objects[i].querySelector('.EllipseInner');
        SVGPath = objects[i].querySelector('.SVGPath');
        NameWrapping = objects[i].querySelector('.NameWrapping');
        if(objects[i].selected == true){
            EllipseInner.style.fill="rgba(51,51,51,1)";
            SVGPath.style.fill="rgba(0,255,176,1)";
            NameWrapping.style.color="rgba(0,255,176,1)";
        }else{
            EllipseInner.style.fill="rgba(0,255,176,1)";
            SVGPath.style.fill="rgba(51,51,51,1)";
            NameWrapping.style.color="rgba(51,51,51,1)";
        }
        objects[i].selected = !objects[i].selected;
    })
}

ObjReset = document.getElementsByClassName('reset');
ObjReset[0].addEventListener('click', function()
{   
    for (let i = 0; i < objects.length; ++i){
        EllipseInner = objects[i].querySelector('.EllipseInner');
        SVGPath = objects[i].querySelector('.SVGPath');
        NameWrapping = objects[i].querySelector('.NameWrapping');
        EllipseInner.style.fill="rgba(51,51,51,1)";
        SVGPath.style.fill="rgba(0,255,176,1)";
        NameWrapping.style.color="rgba(0,255,176,1)";
        objects[i].selected = false;
    }
})

ObjNext = document.getElementById('aNext');
ObjNext.addEventListener('click', function()
{
    keywords = "";
    for (let i = 0; i < objects.length; ++i){
        if (objects[i].selected){
            NameSpan = objects[i].querySelector('.NameSpan');
            keywords = keywords + " " + NameSpan.textContent;
        }
    }
    ObjNext.href = "/project/search/?keywords=" + keywords.trim();
})