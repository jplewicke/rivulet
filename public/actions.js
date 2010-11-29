var actions = new Object;

actions["make_credit_offer"] = new Object;
actions["accept_credit_offer"] = new Object;
actions["make_payment"] = new Object;
actions["make_reserved_payment"] = new Object;
actions["request_payment"] = new Object;
actions["view_credit_balance"] = new Object;

actions["make_credit_offer"].button = "Make Credit Offer"
actions["accept_credit_offer"].button = "Accept Credit Offer"
actions["make_payment"].button = "Make Payment"
actions["make_reserved_payment"].button = "Make Reserved Payment"
actions["request_payment"].button = "Request Payment"
actions["view_credit_balance"].button = "View Credit Balance";


actions["make_credit_offer"].uri = function (curr_user, dest_user) {
    return "/credits/" + curr_user + "/";
};

actions["accept_credit_offer"].uri = function (curr_user, dest_user) {
    return "/credits/" + dest_user + "/";
};

actions["make_payment"].uri = function (curr_user, dest_user) {
    return "/transactions/" + curr_user + "/";
};

actions["make_reserved_payment"].uri = function (curr_user, dest_user) {
    return "/transactions/" + curr_user + "/held/";
};

actions["request_payment"].uri = function (curr_user, dest_user) {
    return "/transactions/" + dest_user + "/held/";
};

actions["view_credit_balance"].uri = function (curr_user, dest_user) {
    return "/credits/" + curr_user + "/?to=dest_user";
};


actions["make_credit_offer"].meth = "POST"
actions["accept_credit_offer"].meth = "POST"
actions["make_payment"].meth = "POST"
actions["make_reserved_payment"].meth = "POST"
actions["request_payment"].meth = "POST"
actions["view_credit_balance"].meth = "GET"

