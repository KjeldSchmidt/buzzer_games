#include <Arduino.h>
#include <HardwareSerial.h>

const int buzzer1_in = 12;
const int buzzer1_out = 2;
const int buzzer2_in = 11;
const int buzzer2_out = 3;

bool pressed = false;
uint8_t current_player;

enum class State {
	IDLE,
	WEBCAM_GAME,
	LIGHT_UP,
	FREEPLAY_WAIT_BUZZER,
};

State state = State::IDLE;

void setup() {
	pinMode( buzzer1_in, INPUT_PULLUP );
	pinMode( buzzer2_in, INPUT_PULLUP );
	pinMode( buzzer1_out, OUTPUT );
	pinMode( buzzer2_out, OUTPUT );

	Serial.begin( 9600 );
}

void init_webcam_game() {
	state = State::WEBCAM_GAME;
	digitalWrite( buzzer1_out, 0 );
	digitalWrite( buzzer2_out, 0 );
	pressed = false;
}

uint8_t get_led_from_player( uint8_t player ) {
	return player == 1 ? buzzer1_out : buzzer2_out;
}

void init_idle() {
	state = State::IDLE;
	digitalWrite( buzzer1_out, 0 );
	digitalWrite( buzzer2_out, 0 );
}

void init_light_up() {
	if ( state != State::WEBCAM_GAME ) return;
	state = State::LIGHT_UP;

	int led_port = get_led_from_player( current_player );
	digitalWrite( led_port, 1 );

	Serial.write( current_player );
}

void init_free_play() {
	state = State::FREEPLAY_WAIT_BUZZER;
	digitalWrite( buzzer1_out, 1 );
	digitalWrite( buzzer2_out, 1 );
	delay( 100 );
	digitalWrite( buzzer1_out, 0 );
	digitalWrite( buzzer2_out, 0 );
}

void process_serial() {
	uint8_t cmd = Serial.read();

	if ( cmd == 'v' ) {
		init_webcam_game();
		return;
	} else if ( cmd == 'i' ) {
		init_idle();
	} else if ( cmd == 'f' ) {
		init_free_play();
	}
}

void check_for_buzzer() {
	if ( !pressed ) {
		if ( !digitalRead( buzzer1_in )) {
			current_player = 1;
			pressed = true;
		}
		if ( !digitalRead( buzzer2_in )) {
			current_player = 2;
			pressed = true;
		}

		if ( pressed ) {
			init_light_up();
		}
	}
}

void check_for_freeplay_buzzer() {
	char second_player;
	if ( !digitalRead( buzzer1_in )) {
		current_player = 1;
		second_player = 2;
	} else if ( !digitalRead( buzzer2_in )) {
		current_player = 2;
		second_player = 1;
	} else {
		return;
	}

	Serial.write( 's' );
	digitalWrite( get_led_from_player( current_player ), HIGH );
	delay( 10000 );
	digitalWrite( get_led_from_player( current_player ), LOW );
	digitalWrite( get_led_from_player( second_player ), HIGH );
	delay( 10000 );
	digitalWrite( get_led_from_player( second_player ), LOW );
	Serial.write( 'c' );
}

void loop() {
	if ( Serial.available() > 0 ) {
		process_serial();
	}

	if ( state == State::WEBCAM_GAME ) {
		check_for_buzzer();
	} else if ( state == State::FREEPLAY_WAIT_BUZZER ) {
		check_for_freeplay_buzzer();
	}
}