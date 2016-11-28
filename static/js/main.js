
var chatApp = angular.module('chatApp', ['ngWebSocket']);
chatApp.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});
chatApp.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});


chatApp.factory('WebSocketChat', ['$websocket', function($websocket) {
    var dataStream = $websocket('ws://' + document.location.host + '/ws');

    var messages = [];
    var users = {};

    dataStream.onMessage(function(message) {
        var data = JSON.parse(message.data);
       
        if (data.users) {
            for (i=0; i<data.users.length; i++) {
                users[data.users[i]['id']] = data.users[i];
            }
        }
        
        if (data.remove_users) {
            for (i=0; i<data.remove_users.length; i++) {
                delete users[data.remove_users[i]['id']];
            }
        }

        if (data.messages)    
            Array.prototype.push.apply(messages, data.messages);

        //console.log(users);
    });

    return {
        users: users,
        messages: messages,
        get: function(text) {
           dataStream.send(JSON.stringify(text));
        }
    };
}]);

chatApp.controller('ChatCtrl', ['$scope', 'WebSocketChat', function($scope, WebSocketChat) {

    $scope.messages = WebSocketChat.messages;
    $scope.users = WebSocketChat.users;
    
    $scope.send = function() {
       // console.log($scope.message);
        
        WebSocketChat.get({'message': {'id': 1, 'text': $scope.form_text}});
        $scope.form_text = '';
    }
}]);  