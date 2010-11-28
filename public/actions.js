var actions = new Object;

actions["make_credit_offer"] = new Object;
actions["accept_credit_offer"] = new Object;
actions["make_payment"] = new Object;
actions["make_reserved_payment"] = new Object;
actions["request_payment"] = new Object;
actions["view_credit_balance"] = new Object;

actions["make_credit_offer"]["label"] = "Make Credit Offer"
actions["accept_credit_offer"]["label"] = "Accept Credit Offer"
actions["make_payment"]["label"] = "Make Payment"
actions["make_reserved_payment"]["label"] = "Make Reserved Payment"
actions["request_payment"]["label"] = "Request Payment"
actions["view_credit_balance"]["label"] = "View Credit Balance";


actions["make_credit_offer"]["uri"] = function (curr_user, dest_user) {
    return "/accounts/" + curr_user;
    };

