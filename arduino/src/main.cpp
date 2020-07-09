#include <Arduino.h>
#include <HardwareSerial.h>

const int buzzer1_in = 12;
const int buzzer1_out = 3;
const int buzzer2_in = 11;
const int buzzer2_out = 2;

bool pressed = false;
int winner;

enum class State {
	IDLE,
	WAIT_FOR_BUZZER,
	LIGHT_UP,
};

State state = State::IDLE;

void setup() {
	pinMode( buzzer1_in, INPUT_PULLUP );
	pinMode( buzzer2_in, INPUT_PULLUP );
	pinMode( buzzer1_out, OUTPUT );
	pinMode( buzzer2_out, OUTPUT );

	Serial.begin( 9600 );
}

void init_wait_for_buzzer() {
	state = State::WAIT_FOR_BUZZER;
	digitalWrite( buzzer1_out, 0 );
	digitalWrite( buzzer2_out, 0 );
	pressed = false;
}

void init_light_up() {
	if ( state != State::WAIT_FOR_BUZZER ) return;
	state = State::LIGHT_UP;

	int led_port = winner == 1 ? buzzer1_out : buzzer2_out;
	digitalWrite( led_port, 1 );

	Serial.println( winner );
}

void process_serial() {
	String cmd = Serial.readString();
	if ( cmd.length() == 0 ) return;

	if ( cmd.equals( "start_buzzer" )) {
		init_wait_for_buzzer();
		return;
	}
}

void check_for_buzzer() {
	if ( !pressed ) {
		if ( !digitalRead( buzzer1_in )) {
			winner = 1;
			pressed = true;
		}
		if ( !digitalRead( buzzer2_in )) {
			winner = 2;
			pressed = true;
		}

		if ( pressed ) {
			init_light_up();
		}
	}
}

void loop() {
	if ( state == State::WAIT_FOR_BUZZER ) {
		check_for_buzzer();
	} else {
		process_serial();
	}
}