ENV['RACK_ENV'] = 'test'

require 'routes'
require 'test/unit'
require 'rack/test'
require "base64"

class RoutesTest < Test::Unit::TestCase
  include Rack::Test::Methods
  def app
    Sinatra::Application
  end

  
  def test_without_authentication
    get '/accounts/User_133'
    assert_equal 401, last_response.status
  end

  def test_with_bad_credentials
    get '/accounts/User_145', {}, {'HTTP_AUTHORIZATION' => encode_credentials('go', 'away')}
    assert_equal 401, last_response.status
  end

  def test_with_proper_credentials
    get '/accounts/User_133', {}, cred(133)
    assert_equal 200, last_response.status
  end
  
  def test_acct_creation
    i = rand(7000)+1000
    uid = "User_#{i}"
    post '/accounts', {:user => uid, :secret => "pw"}, {}
    assert_equal 200, last_response.status
    assert_equal uid, JSON.parse(last_response.body)['user']
    assert_equal 8, JSON.parse(last_response.body)['depth']
    get "/accounts/#{uid}", {}, cred(i)
    assert_equal 200, last_response.status
    assert_equal uid, JSON.parse(last_response.body)['user']
    assert_equal 8, JSON.parse(last_response.body)['depth']
  end
  
  def test_acct_noncreation
    post '/accounts', {:user => "User_200", :secret => "pw"}, {}
    assert_equal 403, last_response.status
  end
  
  def test_acct_creation_depth
    i = rand(7000)+1000
    uid = "User_#{i}"
    get "/accounts/#{uid}", {}, cred(i)
    assert_equal 401, last_response.status
    post '/accounts', {:user => uid, :secret => "pw", :depth => 5}, {}
    assert_equal 200, last_response.status
    assert_equal uid, JSON.parse(last_response.body)['user']
    assert_equal 5, JSON.parse(last_response.body)['depth']
    get "/accounts/#{uid}", {}, cred(i)
    assert_equal 200, last_response.status
    assert_equal uid, JSON.parse(last_response.body)['user']
    assert_equal 5, JSON.parse(last_response.body)['depth']
    #Could also test that correct URLs are returned.
  end
  
  def test_credit_extension_parsefailure_nonnumeric
    post '/credits/User_133', {:to => "User_134", :amount => "dinosaur"}, cred(133)
    assert_equal 400, last_response.status
  end

  def test_credit_extension_parsefailure_tomissing
    post '/credits/User_133', {:user_id => "User_134", :amount => "4.5"}, cred(133)
    assert_equal 400, last_response.status
  end

  def test_credit_extension_parsefailure_amountmissing
    post '/credits/User_133', {:user_id => "User_134"}, cred(133)
    assert_equal 400, last_response.status
  end
  
  def test_credit_ext_parse_nonnegative
    post '/credits/User_383/', {:to => "User_326", :amount => "-1.5"}, cred(383)
    assert_equal 400, last_response.status
  end
  
  def test_credit_ext_parse_positive
    post '/credits/User_383/', {:to => "User_326", :amount => "0"}, cred(383)
    assert_equal 400, last_response.status
  end
  
  def test_credit_extension_auth_failure
    post '/credits/User_133', {:to => "User_134", :amount => 5.4}, cred(167)
    assert_equal 401, last_response.status
  end

  def test_credit_extension
    amt = rand(23) + 0.1
    post '/credits/User_133', {:to => "User_134", :amount => amt}, cred(133)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_offered']
  end

  def test_credit_receipt_parsefailure
    post '/credits/User_133', {:to => "User_134", :amount => "dinosaur"}, cred(134)
    assert_equal 400, last_response.status
  end

  def test_credit_receipt
    amt = rand(23) + 0.1
    post '/credits/User_133', {:to => "User_134", :amount => amt}, cred(134)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_accepted']
  end
  
  def test_payment_auth_failure
    post '/transactions/User_433', {:to => "User_446", :amount => 4.0}, cred(446)
    assert_equal 401, last_response.status
  end
  
  def test_payment_auth_failure2
    post '/transactions/User_433', {:to => "User_446", :amount => 4.0}, bad_cred()
    assert_equal 401, last_response.status
  end
  
  def test_payment_parsefailure_nonnumeric
    post '/transactions/User_433', {:to => "User_446", :amount => "dinosaur"}, cred(433)
    assert_equal 400, last_response.status
  end

  def test_payment_parsefailure_tomissing
    post '/transactions/User_433', {:user_id => "User_446", :amount => "4.5"}, cred(433)
    assert_equal 400, last_response.status
  end

  def test_payment_parsefailure_amountmissing
    post '/transactions/User_433', {:user_id => "User_446"}, cred(433)
    assert_equal 400, last_response.status
  end

  def test_payment_parse_nonnegative
    post '/transactions/User_67', {:to => "User_326", :amount => "-1.5"}, cred(67)
    assert_equal 400, last_response.status
  end
  
  def test_payment_parse_positive
    post '/transactions/User_34', {:to => "User_326", :amount => "0"}, cred(34)
    assert_equal 400, last_response.status
  end
  
  def test_hold_auth_failure
      post '/transactions/User_233/held', {:to => "User_246", :amount => 1.0}, bad_cred()
      assert_equal 401, last_response.status
  end
  
  def test_hold_success
    
  end
  
  def test_hold_success2
    
  end
  
  def test_hold_parse_nonnumeric
    post '/transactions/User_183/held', {:to => "User_326", :amount => "dinosaur"}, cred(183)
    assert_equal 400, last_response.status
  end
  
  def test_hold_parse_tomissing
    post '/transactions/User_183/held', {:amount => "3.5"}, cred(183)
    assert_equal 400, last_response.status
  end
  
  def test_hold_parse_amountmissing
    post '/transactions/User_183/held', {:to => "User_326"}, cred(183)
    assert_equal 400, last_response.status
  end
  
  def test_hold_parse_nonnegative
    post '/transactions/User_183/held', {:to => "User_326", :amount => "-1.5"}, cred(183)
    assert_equal 400, last_response.status
  end
  
  def test_hold_parse_positive
    post '/transactions/User_183/held', {:to => "User_326", :amount => "0"}, cred(183)
    assert_equal 400, last_response.status
  end
  
  def test_comprehensive
    src_id = rand(100000) + 10000
    dest_id = src_id + 1
    
    #Create accounts
    post '/accounts', {:user => "User_#{src_id}", :secret => "pw"}, {}
    assert_equal 200, last_response.status
    post '/accounts', {:user => "User_#{dest_id}", :secret => "pw"}, {}
    assert_equal 200, last_response.status
    
    #Create unaccepted credit.
    amt = 10.0
    post "/credits/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(src_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_offered']
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(src_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_offered']
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(dest_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_offered']
    
    #Verify inability to for src to grant a credit of 5.0 to dest.
    amt = 5.0
    post "/transactions/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(src_id)
    assert_equal 403, last_response.status
    
    #Accept partial credit.
    amt = 8.0
    post "/credits/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(dest_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_accepted']
    
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(src_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_accepted']
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(dest_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_accepted']
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(79)
    assert_equal 401, last_response.status
    
    #Use part of the credit line.
    amt = 4.0
    post "/transactions/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(src_id)
    assert_equal 200, last_response.status
    #puts last_response.body
    assert_equal 4.0, JSON.parse(last_response.body)['max_credit_line']
    assert_equal 4.0, JSON.parse(last_response.body)['max_debit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    assert_equal 0.0, JSON.parse(last_response.body)['credit_held']
    
    
    #Accept full credit.
    amt = 10.0
    post "/credits/User_#{src_id}", {:to => "User_#{dest_id}", :amount => amt}, cred(dest_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_accepted']
    assert_equal 6.0, JSON.parse(last_response.body)['max_credit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    assert_equal 0.0, JSON.parse(last_response.body)['credit_held']
    
    
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(dest_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_accepted']
    assert_equal 6.0, JSON.parse(last_response.body)['max_credit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    assert_equal 0.0, JSON.parse(last_response.body)['credit_held']
    
    get "/credits/User_#{src_id}", {:to => "User_#{dest_id}"}, cred(src_id)
    assert_equal 200, last_response.status
    assert_equal amt, JSON.parse(last_response.body)['credit_accepted']
    assert_equal 6.0, JSON.parse(last_response.body)['max_credit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    assert_equal 0.0, JSON.parse(last_response.body)['credit_held']
    
    #Give back that 4.0 of credit.
    amt = 4.0
    post "/transactions/User_#{dest_id}", {:to => "User_#{src_id}", :amount => amt}, cred(dest_id)
    assert_equal 200, last_response.status
    assert_equal 10.0, JSON.parse(last_response.body)['max_debit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['max_credit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    assert_equal 0.0, JSON.parse(last_response.body)['credit_held']
    
    
    get "/credits/User_#{dest_id}", {:to => "User_#{src_id}"}, cred(src_id)
    assert_equal 200, last_response.status
    assert_equal 10.0, JSON.parse(last_response.body)['max_debit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['max_credit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    assert_equal 0.0, JSON.parse(last_response.body)['credit_held']
    get "/credits/User_#{dest_id}", {:to => "User_#{src_id}"}, cred(dest_id)
    assert_equal 200, last_response.status
    assert_equal 10.0, JSON.parse(last_response.body)['max_debit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['max_credit_line']
    assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    assert_equal 0.0, JSON.parse(last_response.body)['credit_held']
    
    
    #Reserve some of that there credit.
    amt = 3.0
    post "/transactions/User_#{src_id}/held", {:to => "User_#{dest_id}", :amount => amt}, cred(dest_id)
    assert_equal 200, last_response.status
    puts last_response.body
    #assert_equal 0.0, JSON.parse(last_response.body)['max_debit_line']
    assert_equal 7.0, JSON.parse(last_response.body)['max_credit_line']
    #assert_equal 0.0, JSON.parse(last_response.body)['debit_held']
    #assert_equal 0.0, JSON.parse(last_response.body)['credit_held']
    
    # Should fail
    post "/transactions/User_#{src_id}", {:to => "User_#{dest_id}", :amount => 8.0}, cred(src_id)
    assert_equal 403, last_response.status
    
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