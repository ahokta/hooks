<?php
header('Content-Type: application/json');
	$header = apache_request_headers();

	// Configuration
    $oktadomain = "https://myoktatenant.oktapreview.com";
    $logfile = "/tmp/logfile.log";
    $secret = "0d1a88d94a1653c35cdafa9a5eb2b9aa"; // Secret set for this Hook, use X-Okta-Verification as header

	function OktaAuthNlogin($username, $password, $oktadomain) {
	    $json = ["username" => $username, "password" => $password];
	    $encodedJSON = json_encode($json);

        $options = array(
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HEADER         => false,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_MAXREDIRS      => 10,
            CURLOPT_AUTOREFERER    => true,
            CURLOPT_SSL_VERIFYPEER => false, // can be turned on, if official certs were issued
            CURLOPT_CUSTOMREQUEST  => "POST",
            CURLOPT_POSTFIELDS         => $encodedJSON,
            CURLOPT_HTTPHEADER         => array('Content-Type: application/json; charset=utf-8', 'Content-Length: ' . strlen($encodedJSON))
        );

        $ch = curl_init($oktadomain . "/api/v1/authn");

        curl_setopt_array($ch, $options);
        $response = curl_exec($ch);

        if (curl_errno($ch)) {
           $error_msg = curl_error($ch);
        }
        curl_close($ch);
        if (isset($error_msg)) {
            echo $error_msg;
        } else {
           return $response;
        }
	}

	// Okta Authentication
        if (isset($header["X-Okta-Verification"])) {
	    $verify_secret = $header["X-Okta-Verification"];
	} else {
	    $verify_secret = "";
	}

	// Verify Secret
	if (strcmp ($verify_secret, $secret) != 0) {
   		header("HTTP/1.1 401 Unauthorized");
   		exit(0);
	}

	// Read input
	$json = file_get_contents('php://input');
    $jsonobject = json_decode($json, true);

    // Write logfile for Debug
    //file_put_contents($file, $json);

    $username = $jsonobject["data"]["context"]["credential"]["username"];
	$password = $jsonobject["data"]["context"]["credential"]["password"];

	// Check username + password and send VERIFIED if login was successful
	$result = OktaAuthNlogin($username, $password, $oktadomain);
	$jsonobject = json_decode($result, true);
	$status =  $jsonobject["status"];

	if (strcmp("SUCCESS", $status) === 0) {
	    $data = ["commands" =>[["type" => "com.okta.action.update","value" => ["credential" => "VERIFIED"]]]];
	} else {
	    $data = ["commands" =>[["type" => "com.okta.action.update","value" => ["credential" => "UNVERIFIED"]]]];
	}
	echo json_encode($data);
?>
