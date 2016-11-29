
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

    var profile = {},
        messages = [],
        users = {'All': {
            'login': 'All'
        }};

    dataStream.onMessage(function(message) {
        var data = JSON.parse(message.data);
       
        if (data.profile) {
            profile['login'] = data.profile['login'];
        }

        if (data.users) {
            for (i=0; i<data.users.length; i++) {
                users[data.users[i]['login']] = data.users[i];
            }
        }
        
        if (data.remove_users) {
            for (i=0; i<data.remove_users.length; i++) {
                delete users[data.remove_users[i]['login']];
            }
        }

        if (data.messages)    
            Array.prototype.push.apply(messages, data.messages);
    });

    return {
        profile: profile,
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
    $scope.profile = WebSocketChat.profile;
    $scope.user_to = $scope.users['All'];
    
    $scope.send = function() {
        WebSocketChat.get({'message': {'to': $scope.user_to['login'], 'text': $scope.form_text}});
        $scope.form_text = '';
    }

    $scope.select_user_to = function(user) {
        if (user['login'] != $scope.profile.login)
            $scope.user_to = user;
    }
}]); 