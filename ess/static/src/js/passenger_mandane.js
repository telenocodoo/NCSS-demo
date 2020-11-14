// Capture the form submit button
$("#submit_button_id").click(function(event){
  event.preventDefault();
  // Get form data
  var form_data = $("#contactForm1").serialize();
  var errmsg = $('#error_msg');
  var post_url = window.location.href;
  console.log(form_data)
  console.log(post_url)
  // Sending a POST request to Moyasar API using AJAX
  $.ajax({
  url: post_url,
  type: "post",
  data: form_data,
//  dataType: "json",
})
// uses `.done` callback to handle a successful AJAX request
.done(function(data) {
// Here we will handle JSON response and do step3 & step4
var payment_id = data.id;
// Redirect the user to transaction_url
var str=$("#course_type").val
 console.log(str);
if (['internal', 'external', 'private'].indexOf(str) >= 0)
 errmsg.text('Your Request has been Sent Successfully');
else
    errmsg.text('تم ارسال طلبكم بنجاح');
})
.fail(function (data) {
                    console.log('An error occurred.');
                console.log(data);
                errmsg.text(' Wrong With your Request ');
                });
});


$("#course_type").change(function(){
 var errmsg = $('#error_msg');
   if($(this).val()=="private" || $(this).val()==  "خاصة")
   {
       $("div#start_date").show();
       $("div#end_date").show();
         errmsg.text('');

   }
    else
    {
     errmsg.text('');
        $("div#start_date").hide();
        $("div#end_date").hide();

    }
});
//
//$("#submit_button_id").submit(function(event){
//	event.preventDefault(); //prevent default action
//	var post_url = $(this).attr("action"); //get form action url
//	var request_method = $(this).attr("method"); //get form GET/POST method
//	var form_data = $(this).serialize(); //Encode form elements for submission
//
//	$.ajax({
//		url : post_url,
//		type: request_method,
//		data : form_data
//	}).done(function(response){ //
//		$("#server-results").html(response);
//	});
//});