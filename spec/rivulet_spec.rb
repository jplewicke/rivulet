require File.dirname(__FILE__) + '/spec_helper'
 
describe "Routes" do
  include Rack::Test::Methods
  def app
      Sinatra::Application
    end
  
    it "should require authentication to view user info" do
      get '/accounts/User_133'
      last_response.status.should == 401
    end
 
  it "should respond to /" do
    get '/'
    last_response.should be_ok
  end
  

  it "should test_without_authentication"  do
    get '/accounts/User_133'
    last_response.status.should == 401 
  end

  it "should test_with_bad_credentials"  do
    get '/accounts/User_145', {}, {'HTTP_AUTHORIZATION' => encode_credentials('go', 'away')}
    last_response.status.should == 401 
  end

  it "should test_with_proper_credentials"  do
    get '/accounts/User_133', {}, cred(133)
    last_response.status.should == 200 
  end

  it "should test_acct_creation"  do
    i = rand(7000)+1000
    uid = "User_#{i}"
    post '/accounts', {:user => uid, :secret => "pw"}, {}
    last_response.status.should == 200 
    JSON.parse(last_response.body)['user'].should == uid 
    JSON.parse(last_response.body)['depth'].should == 8 
    get "/accounts/#{uid}", {}, cred(i)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['user'].should == uid 
    JSON.parse(last_response.body)['depth'].should == 8 
  end

  it "should test_acct_noncreation"  do
    post '/accounts', {:user => "User_200", :secret => "pw"}, {}
    last_response.status.should == 403 
  end

  it "should test_acct_creation_depth"  do
    i = rand(7000)+1000
    uid = "User_#{i}"
    get "/accounts/#{uid}", {}, cred(i)
    last_response.status.should == 401 
    post '/accounts', {:user => uid, :secret => "pw", :depth => 5}, {}
    last_response.status.should == 200 
    JSON.parse(last_response.body)['user'].should == uid 
    JSON.parse(last_response.body)['depth'].should == 5 
    get "/accounts/#{uid}", {}, cred(i)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['user'].should == uid 
    JSON.parse(last_response.body)['depth'].should == 5 
    #Could also test that correct URLs are returned.
  end

  it "should test_credit_extension_parsefailure_nonnumeric"  do
    post '/credits/User_133', {:to => "User_134", :amount => "dinosaur"}, cred(133)
    last_response.status.should == 400 
  end

  it "should test_credit_extension_parsefailure_tomissing"  do
    post '/credits/User_133', {:user_id => "User_134", :amount => "4.5"}, cred(133)
    last_response.status.should == 400 
  end

  it "should test_credit_extension_parsefailure_amountmissing"  do
    post '/credits/User_133', {:user_id => "User_134"}, cred(133)
    last_response.status.should == 400 
  end

  it "should test_credit_ext_parse_nonnegative"  do
    post '/credits/User_383/', {:to => "User_326", :amount => "-1.5"}, cred(383)
    last_response.status.should == 400 
  end

  it "should test_credit_ext_parse_positive"  do
    post '/credits/User_383/', {:to => "User_326", :amount => "0"}, cred(383)
    last_response.status.should == 400 
  end

  it "should test_credit_extension_auth_failure"  do
    post '/credits/User_133', {:to => "User_134", :amount => 5.4}, cred(167)
    last_response.status.should == 401 
  end

  it "should test_credit_extension"  do
    amt = rand(23) + 0.1
    post '/credits/User_133', {:to => "User_134", :amount => amt}, cred(133)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_offered'].should == amt 
  end

  it "should test_credit_receipt_parsefailure"  do
    post '/credits/User_133', {:to => "User_134", :amount => "dinosaur"}, cred(134)
    last_response.status.should == 400 
  end

  it "should test_credit_receipt"  do
    amt = rand(23) + 0.1
    post '/credits/User_133', {:to => "User_134", :amount => amt}, cred(134)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_accepted'].should == amt 
  end

  it "should test_payment_auth_failure"  do
    post '/transactions/User_433', {:to => "User_446", :amount => 4.0}, cred(446)
    last_response.status.should == 401 
  end

  it "should test_payment_auth_failure2"  do
    post '/transactions/User_433', {:to => "User_446", :amount => 4.0}, bad_cred()
    last_response.status.should == 401 
  end

  it "should test_payment_parsefailure_nonnumeric"  do
    post '/transactions/User_433', {:to => "User_446", :amount => "dinosaur"}, cred(433)
    last_response.status.should == 400 
  end

  it "should test_payment_parsefailure_tomissing"  do
    post '/transactions/User_433', {:user_id => "User_446", :amount => "4.5"}, cred(433)
    last_response.status.should == 400 
  end

  it "should test_payment_parsefailure_amountmissing"  do
    post '/transactions/User_433', {:user_id => "User_446"}, cred(433)
    last_response.status.should == 400 
  end

  it "should test_payment_parse_nonnegative"  do
    post '/transactions/User_67', {:to => "User_326", :amount => "-1.5"}, cred(67)
    last_response.status.should == 400 
  end

  it "should test_payment_parse_positive"  do
    post '/transactions/User_34', {:to => "User_326", :amount => "0"}, cred(34)
    last_response.status.should == 400 
  end

  it "should test_hold_auth_failure"  do
    post '/transactions/User_233/held', {:to => "User_246", :amount => 1.0}, bad_cred()
    last_response.status.should == 401 
  end

  it "should test_hold_success"  do

  end

  it "should test_hold_success2"  do

  end

  it "should test_hold_parse_nonnumeric"  do
    post '/transactions/User_183/held', {:to => "User_326", :amount => "dinosaur"}, cred(183)
    last_response.status.should == 400 
  end

  it "should test_hold_parse_tomissing"  do
    post '/transactions/User_183/held', {:amount => "3.5"}, cred(183)
    last_response.status.should == 400 
  end

  it "should test_hold_parse_amountmissing"  do
    post '/transactions/User_183/held', {:to => "User_326"}, cred(183)
    last_response.status.should == 400 
  end

  it "should test_hold_parse_nonnegative"  do
    post '/transactions/User_183/held', {:to => "User_326", :amount => "-1.5"}, cred(183)
    last_response.status.should == 400 
  end

  it "should test_hold_parse_positive"  do
    post '/transactions/User_183/held', {:to => "User_326", :amount => "0"}, cred(183)
    last_response.status.should == 400 
  end

  it "should test_comprehensive"  do
    src_id = rand(100000) + 10000
    dest_id = src_id + 1

    #Create accounts
    post '/accounts', {:user => "User_#{src_id}", :secret => "pw"}, {}
    last_response.status.should == 200 
    post '/accounts', {:user => "User_#{dest_id}", :secret => "pw"}, {}
    last_response.status.should == 200 

    #Create unaccepted credit.
    amt = 10.0
    post "/credits/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(src_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_offered'].should == amt 
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(src_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_offered'].should == amt 
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(dest_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_offered'].should == amt 

    #Verify inability to for src to grant a credit of 5.0 to dest.
    amt = 5.0
    post "/transactions/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(src_id)
    last_response.status.should == 403 

    #Accept partial credit.
    amt = 8.0
    post "/credits/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(dest_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_accepted'].should == amt 

    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(src_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_accepted'].should == amt 
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(dest_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_accepted'].should == amt 
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(79)
    last_response.status.should == 401 

    #Use part of the credit line.
    amt = 4.0
    post "/transactions/User_#{dest_id}", {:to => "User_#{src_id}", :amount => amt}, cred(dest_id)
    last_response.status.should == 200 
    #puts last_response.body
    JSON.parse(last_response.body)['max_credit_line'].should == 4.0 
    JSON.parse(last_response.body)['max_debit_line'].should == 4.0 
    JSON.parse(last_response.body)['debit_held'].should == 0.0 
    JSON.parse(last_response.body)['credit_held'].should == 0.0 

    get "/accounts/User_#{src_id}", {}, cred(src_id)
    last_response.status.should == 200
    JSON.parse(last_response.body)['balance'].should == 4.0
    
    get "/accounts/User_#{dest_id}", {}, cred(dest_id)
    last_response.status.should == 200
    JSON.parse(last_response.body)['balance'].should == -4.0

    #Accept full credit.
    amt = 10.0
    post "/credits/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(dest_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_accepted'].should == amt 
    JSON.parse(last_response.body)['max_credit_line'].should == 6.0 
    JSON.parse(last_response.body)['debit_held'].should == 0.0 
    JSON.parse(last_response.body)['credit_held'].should == 0.0 


    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(dest_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_accepted'].should == amt 
    JSON.parse(last_response.body)['max_credit_line'].should == 6.0 
    JSON.parse(last_response.body)['debit_held'].should == 0.0 
    JSON.parse(last_response.body)['credit_held'].should == 0.0 

    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(src_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['credit_accepted'].should == amt 
    JSON.parse(last_response.body)['max_credit_line'].should == 6.0 
    JSON.parse(last_response.body)['debit_held'].should == 0.0 
    JSON.parse(last_response.body)['credit_held'].should == 0.0 

    #Give back that 4.0 of credit.
    amt = 4.0
    post "/transactions/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(src_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['max_debit_line'].should == 10.0 
    JSON.parse(last_response.body)['max_credit_line'].should == 0.0 
    JSON.parse(last_response.body)['debit_held'].should == 0.0 
    JSON.parse(last_response.body)['credit_held'].should == 0.0 


    get "/credits/User_#{dest_id}", {:to => "User_#{src_id}"}, cred(src_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['max_debit_line'].should == 10.0 
    JSON.parse(last_response.body)['max_credit_line'].should == 0.0 
    JSON.parse(last_response.body)['debit_held'].should == 0.0 
    JSON.parse(last_response.body)['credit_held'].should == 0.0 
    get "/credits/User_#{dest_id}", {:to => "User_#{src_id}"}, cred(dest_id)
    last_response.status.should == 200 
    JSON.parse(last_response.body)['max_debit_line'].should == 10.0 
    JSON.parse(last_response.body)['max_credit_line'].should == 0.0 
    JSON.parse(last_response.body)['debit_held'].should == 0.0 
    JSON.parse(last_response.body)['credit_held'].should == 0.0 


    #Reserve some of that there credit.
    amt = 3.0
    post "/transactions/User_#{dest_id}/held", {:to => "User_#{src_id}", :amount => amt}, cred(dest_id)
    last_response.status.should == 200 
    puts last_response.body
    #assert_equal 0.0, JSON.parse(last_response.body)['max_debit_line']
    JSON.parse(last_response.body)['max_credit_line'].should == 7.0 
    #assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    #assert_equal 0.0, JSON.parse(last_response.body)['credit_held']

    # Should fail
    post "/transactions/User_#{dest_id}", {:to => "User_#{src_id}", :amount => 8.0}, cred(dest_id)
    last_response.status.should == 403 

    post "/transactions/User_#{dest_id}", {:to => "User_#{src_id}", :amount => 2.0}, cred(dest_id)

    #puts last_response.body
    #assert_equal 403, last_response.status

  end
  
  private

  def encode_credentials(username, password)
    "Basic " + Base64.encode64("#{username}:#{password}")
  end
  
  def cred(uid)
    return {'HTTP_AUTHORIZATION'=> encode_credentials("User_#{uid}", 'pw')}
  end
  
  def bad_cred
    {'HTTP_AUTHORIZATION'=> encode_credentials("go", 'away')}
  end
end

