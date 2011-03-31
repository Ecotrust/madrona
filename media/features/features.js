if(typeof lingcod == 'undefined'){
    lingcod = {};
}
lingcod.features = {};

lingcod.features.model = function(kmlObject){
    // console.log(kmlObject.getName(), kmlObject.getId());
    return kmlObject.getId().match(/(\w+)_\d/)[1];
}