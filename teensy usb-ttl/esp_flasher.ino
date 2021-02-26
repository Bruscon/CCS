#define TIMEOUT 5000 // mS



void setup()
{
  delay(5000);
  Serial.begin(115200);
  Serial1.begin(115200);

/*
  SendCommand("AT+CWMODE=1","OK");
  SendCommand("AT+CIFSR", "OK");
  SendCommand("AT+CIPMUX=1","OK");
  SendCommand("AT+CIPSERVER=1,80","OK");
*/
}

void loop()
{
  /* send everything received from the hardware uart to usb serial & vv */
  if (Serial.available() > 0) {
    char ch = Serial.read();
    Serial1.print(ch);
  }
  if (Serial1.available() > 0) {
    char ch = Serial1.read();
    Serial.print(ch);
  }

/*
  delay(1000);
  Serial1.println("AT+CIPSEND=0,23");
  Serial1.println("\nButton was pressed!\n");
  delay(1000);
  SendCommand("AT+CIPCLOSE=0","OK");
*/
}

boolean SendCommand(String cmd, String ack){
  Serial1.println(cmd); // Send "AT+" command to module
  if (!echoFind(ack)) // timed out waiting for ack string
    return true; // ack blank or ack found
}
 
boolean echoFind(String keyword){
 byte current_char = 0;
 byte keyword_length = keyword.length();
 long deadline = millis() + TIMEOUT;
 while(millis() < deadline){
  if (Serial1.available()){
    char ch = Serial1.read();
    Serial.write(ch);
    if (ch == keyword[current_char])
      if (++current_char == keyword_length){
       Serial.println();
       return true;
    }
   }
  }
 return false; // Timed out
}
