var div = document.getElementById('content_div');

// function linkClicked(stateCallback){
//     alert('link clicked');
//     stateUpdated();
// //        gadgets.rpc.call('top', 'show_snapshot', null, snapshot);
// }

// function buttonClicked() {
//   var value = parseInt(wave.getState().get('count', '0'));
//   wave.getState().submitDelta({'count': value + 1});
// }


function stateUpdated() {
    // console.log('stateUpdated');
    var snapshot = wave.getState().get('snapshot');
    if(snapshot && snapshot != false){
        // console.log('gadget: found snapshot');
        enterFinishedState();
//            gadgets.rpc.call('top', 'show_snapshot', null, snapshot);
    }else{
        // console.log('gadget: didnt find snapshot');
        if(wave.getViewer() == wave.getHost()){
            // console.log('viewer is host');
            enterHostCreationState();
        }else{
            // console.log('viewer is not host');
            enterViewerCreationState();
        }
//            gadgets.rpc.call('top', 'sync_snapshot', function(snapshot){
//                console.log('from gadget, sync_snapshot callback');
//            });
    }
}

var m;

function init() {
    gadgets.window.adjustHeight();
    m = new lingcod.gadgetMessenger.gadgetSide(window.app_url);
    $(m).bind('message', function(e, data){
        if(data.message == 'setSnapshot'){
            wave.getState().submitDelta({'snapshot': gadgets.json.stringify(data)});
        }else{
            console.error('gadget: invalid message');
        }
    });
    // $(window).bind('message', function(e){
    //     var e = e.originalEvent;
    //     if(e.source == top){
    //         var data = gadgets.json.parse(e.data);
    //         if(data.message == 'setSnapshot'){
    //             console.log('gadget: setSnapshot in message', data.camera);
    //             wave.getState().submitDelta({'snapshot': e.data});
    //         }else{
    //             console.error('gadget: invalid message');
    //         }
    //     }else{
    //         // do nothing
    //     }
    // });
    
    $('#show').click(function(e){
        var snapshot = wave.getState().get('snapshot');
        // console.log('snapshot', snapshot);
        var snapshot = gadgets.json.parse(wave.getState().get('snapshot'));
        snapshot.message = 'displaySnapshot';
        m.send(snapshot);
        // var message = gadgets.json.stringify(snapshot);
        // console.log('gadget: displaySnapshot', message);
        // top.postMessage(message, window.app_url);
        e.preventDefault(); 
    });
    
    $('#reset').click(function(e){
        wave.getState().submitDelta({'snapshot': null});
        enterHostCreationState();
        e.preventDefault(); 
    });
    
    // top.postMessage('hi there from the gadget', 'http://mm-01.msi.ucsb.edu/');

    if (wave && wave.isInWaveContainer()) {
        wave.setStateCallback(stateUpdated);
    }
}

/**
 * Changes Gadgets visual state to reflect that another viewer owns this 
 * snapshot gadget, and is still finishing it's creation.
 */
function enterViewerCreationState(){
    $('#creating').show();
    gadgets.window.adjustHeight();
}

function enterHostCreationState(){
    // console.log('enterHostCreationState');
    $('#creating').hide();
    $('#finished').hide()
    $('#options').show();
    $('#creation_instructions').show();
    $('#creation_instructions button').attr('disabled', false);
    
    $('#creation_instructions button').click(function(){
        $(this).attr('disabled', true);
        top.postMessage('{"message": "getSnapshot"}', window.app_url);
    });
    gadgets.window.adjustHeight();
    // $('#creation_form').show();
}

function enterFinishedState(){
    $('#creating').hide();
    $('#options').hide();
    $('#creation_instructions').hide();
    $('#finished').show();
    gadgets.window.adjustHeight();
}

gadgets.util.registerOnLoadHandler(init);