var ta;
var t1;
var t2;
var tb;
var n1;
var n2;
var n2_c;
var bp;
var lp;
var l_l;//reference to left bracket and text
var l_l_t;//reference to left text
var r_l_t;//reference to right text
var JSONstring;
var myJSONObject = {"from":"Alice","to":"Bob","credit_accepted":9.0,"credit_offered":10.0,"debit_accepted":0.0,"debit_offered":0.0,"credit_offered":7.0,"credit_accepted":2.0,"credit_held":0.0,"debit_held":0.0,"net_owed":2.0};
function prepare(){
   var S=document.getElementById("sv");
   var SD=S.getSVGDocument();
   t1=SD.getElementById('text1');
   t2=SD.getElementById('text2');
   tb=SD.getElementById('balanceText');
   n1=SD.getElementById('Node1');
   n2=SD.getElementById('Node2');
   n2_c=SD.getElementById('Node2_circle');
   lp=SD.getElementById('Line_Point');
   l_l=SD.getElementById('leftLimit');
   l_l_t=SD.getElementById('leftLimitText');
   r_l=SD.getElementById('rightLimit');
   r_l_t=SD.getElementById('rightLimitText');
   bp=SD.getElementById('balancePoint');
   ta= document.getElementById('resultTextArea');
   parse_JSON(ta);
}

function parse_JSON(ref_to_text_area){
   JSONstring = ref_to_text_area.value;
   myJSONObject = eval('(' + JSONstring + ')');// eval is unsafe, to be replaced ?? myJSONObject = JSON.parse(JSONstring, reviver); non funziona, forse devo importare qualche libreria??
   myJSONObject.net_owed = -myJSONObject.net_owed//inversion of owed: ?? in Rivulet net_owed=3 means "to" is owed 3 by "from"
}


function change(v){
    n2_c.setAttribute("fill", v);
}
function changeText(ref,value){
    var VariableString = ref.firstChild;
    VariableString.nodeValue = value ; 
}


function balanceToString(from,to,balance,curr){
   var balString =  "none";
   if (balance > 0)        { balString =  from + " owes " + balance + curr + " to " + to + "." ;
   }
   else if (balance < 0)   { balString =  from + " is owed " + ((-1) * balance) + curr + " by " + to + "." ;
   }
   else   { balString =  from + " and " + to + " are even.";
   }
   //alert("Created string:" + balString);
   return balString; //  returns a string describing balance
}
function set_balance_text(from,to,balance,curr) {
   var bs = balanceToString(from,to,balance,curr);
  //alert(bs);
  changeText(tb,bs);
}
//interprets the JSON answer to an action and Draws a diagram
function interpretVisualize() {
    parse_JSON(ta);
    if (myJSONObject.from != null && myJSONObject.to != null ){
        var scaleFactor = 45 / Math.max( 1, Math.abs(myJSONObject.net_owed), Math.min(myJSONObject.credit_accepted,myJSONObject.credit_offered),Math.min(myJSONObject.debit_accepted,myJSONObject.debit_offered));//calculate max between balace point and limits
        //calculate and set position of elements, set visibilities
        n1.setAttribute("display","inline");
        n2.setAttribute("display","inline");
        lp.setAttribute("display","inline");
        //move left limit
        var l_l_translate_str = (-1 * Math.min(myJSONObject.credit_accepted,myJSONObject.credit_offered) * scaleFactor);//calculate move for left limit
        l_l.setAttribute("display","inline");
        l_l.setAttribute("transform","translate(" + l_l_translate_str +", 0 )");
        //left limit text
        changeText(l_l_t, Math.min(myJSONObject.credit_accepted,myJSONObject.credit_offered));
        //move right limit
        var r_l_translate_str = (+1 * Math.min(myJSONObject.debit_accepted,myJSONObject.debit_offered) * scaleFactor);//calculate move for left limit
        r_l.setAttribute("display","inline");
        r_l.setAttribute("transform","translate(" + r_l_translate_str +", 0 )");
        //right limit text
        changeText(r_l_t, Math.min(myJSONObject.debit_accepted,myJSONObject.debit_offered));
        //balance text
        set_balance_text(myJSONObject.from , myJSONObject.to , myJSONObject.net_owed ,'')
        changeText(t1,myJSONObject.from);
        changeText(t2,myJSONObject.to);
        //move balance point
        bp.setAttribute("transform","translate(" + (myJSONObject.net_owed * scaleFactor) +", 0 )");
        }
    else if ( myJSONObject.user != null ){
        n1.setAttribute("display","inline");
        n2.setAttribute("display","none");
        lp.setAttribute("display","none");
        l_l.setAttribute("display","none");
        r_l.setAttribute("display","none");
        changeText(t1,myJSONObject.user);
        changeText(tb,"");
        }
    else {
        n1.setAttribute("display","none");
        n2.setAttribute("display","none");
        lp.setAttribute("display","none");
        l_l.setAttribute("display","none");
        r_l.setAttribute("display","none");
        changeText(tb,"");
        alert("non trovati from to user");
        }
}
