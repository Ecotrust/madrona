if(typeof lingcod == 'undefined'){
    lingcod = {};
}
lingcod.features = {};

lingcod.features.model = function(kmlObject){
    return kmlObject.getId().match(/(\w+)_\d/)[1];
};