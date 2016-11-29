
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
    //token = '1111';
    var dataStream = $websocket('ws://' + document.location.host + '/ws?token=' + token);

    var profile = {},
        messages = [],
        users = {};

    dataStream.onMessage(function(message) {
        var data = JSON.parse(message.data);
        console.log(data);
       
        if (data.profile) {
            profile['login'] = data.profile['login'];
            profile['name'] = data.profile['name'];
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

        if (data.error) {
            alert(data.error);
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
    $scope.users_to = [];
    
    $scope.send = function() {
        WebSocketChat.get({'message': {'to': $scope.users_to, 'text': $scope.form_text}});
        $scope.form_text = '';
    }

    $scope.select_user_to = function(login) {
        if (login != $scope.profile.login)
        {
            if (login == 'all')   
                $scope.users_to = [];
            else if ($scope.users_to.indexOf(login) == -1)
                $scope.users_to.push(login);
            else
                $scope.users_to.splice($scope.users_to.indexOf(login), 1);
        }
    }
}]); 


chatApp.filter('utcToLocal', utcToLocal);
function utcToLocal($filter) {
    return function (date, format) {
        if (!date) return '';
        date = new Date(date);
        var offset = date.getTimezoneOffset() / 60,
            hours = date.getHours();
        date.setHours(hours - offset);
        return $filter('date')(date, format);
    };
}