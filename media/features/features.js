if(typeof madrona == 'undefined'){
    madrona = {};
}
madrona.features = {};

madrona.features.model = function(kmlObject){
    var id = kmlObject.getId();
    if(!id){
        return false;
    }
    var matches = id.match(/(\w+)_\d+/);
    if(matches.length){
        return matches[1];
    }else{
        return false;
    }
};