Alice would like to sign up for an account.
 - POST to rivulet.com/accounts
 - name=alice&password=alice_password
 

 Alice says she will offer up to 10.0 in credit to Bob.
  - POST to rivulet.com/alice/credits
  - HTTP_AUTH name=alice&password=alice_password
  - to=bob&amount=10.0
  - returns rivulet.com/alice/credits/189789a4
  - for now? rivulet.com/alice/credits/bob
  
 Bob says he will go up to 9.5 in debt to Alice.
  - POST to rivulet.com/alice/credits
  - HTTP_AUTH name=bob&password=bob_password
  - to=bob&amount=9.5
  - returns rivulet.com/alice/credits/189789a4
  - for now? rivulet.com/alice/credits/bob


Alice would like to credit 4.0 to Bob immediately for work done or as a gift.
 - POST to rivulet.com/alice/transactions
 - HTTP_AUTH name=alice&password=alice_password
 - to=bob&amount=4.0
 - returns rivulet.com/alice/transactions/294d23
 - for now? rivulet.com/alice/transactions/bob

Bob would like to reserve 5.5 in credit from Alice for work he plans to do for her.
  - POST to rivulet.com/alice/transactions/held
  - HTTP_AUTH name=bob&password=bob_password
  - to=bob&amount=5.5&memo=for_the_carpentry_im_doing
  - returns rivulet.com/alice/transactions/held/6826861f3
  - for now? rivulet.com/alice/transactions/held/bob

Alice would like to free up 3.0 in credit that was reserved for Bob, since his amount of work
was reduced.
 - PUT to rivulet.com/alice/transactions/held/6826861f3
 - HTTP_AUTH name=alice&password=alice_password
 - to=bob&amount=2.5&memo=for_the_carpentry_hes_doing
 - returns rivulet.com/alice/transactions/held/6826861f3, and maybe the updated result



Alice would like to finalize a reserved payment of 2.5 to Bob.
- POST to rivulet.com/alice/transactions/held/6826861f3
- HTTP_AUTH name=alice&password=alice_password
- to=bob&amount=2.5&memo=for_the_carpentry_hes_done
- returns rivulet.com/alice/transactions/187f34




Information

Alice would like to know what her credit/debit balance is with everyone else.
 - GET to rivulet.com/alice/credits
 - HTTP_AUTH name=alice&password=alice_password
 - returns JSON list of balances wrt Alice
 
Bob wants to find out his balance with Alice.
 - GET to rivulet.com/alice/credits
 - HTTP_AUTH name=bob&password=bob_password

Alice wants to find out who has reserved credit from her.
 - GET to rivulet.com/alice/transactions/held
 - HTTP_AUTH name=alice&password=alice_password
 - returns JSON list of holds wrt Alice













