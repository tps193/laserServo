#include <msp430.h>
#include <math.h>

#define BUTTON   BIT3 // Port 1.3

volatile int max;
volatile int h;
volatile float dt;

volatile int lastX;
volatile int lastY;

void delay(volatile unsigned long i)
{
	P1OUT ^= BIT0;


//	volatile unsigned long i;
//	i = 49999;
	do (i--);
	while (i != 0);
}

void init(int minImpulseLength, int maxImpulseLength, int height) {
	max = maxImpulseLength;
	dt = (maxImpulseLength - minImpulseLength) / 3.14f;
	h = height;
	// setting 1500 is 1.5ms is 0deg. servo pos
	TA0CCR1 = 1500;                            // CCR1 PWM duty cycle
	TA1CCR1 = 1500;                            // CCR1 PWM duty cycle
	lastX = 0;
	lastY = 0;
	delay(49000);
}

void regularDelay(void) {
	delay(20000);
}

int getAngle(int x, int y) {
	int b = cos(x);
	return b;
}

void setPosition1(int angle) {
	TA0CCR1 = angle;
}

void setPosition2(int angle) {
	TA1CCR1 = angle;
}

void setPosition(int x, int y) {
	if (x== 0 && y == 0) {
		setPosition1(1500);
		setPosition2(2300);
		return;
	}
	float horizontalServoTime = max - dt * atan2f(y, x);
	float verticalServoTime = max - dt * atan2f(y, h);
	setPosition1(horizontalServoTime);
	setPosition2(verticalServoTime);
	lastX = x;
	lastY = y;
}

void smoothTo(int x1, int y1, int x, int y) {
	int i;
	for (i = 1; i < 11; i++) {
		setPosition(x1 + (x-x1)/10*i, y1 + (y-y1)/10*i);
		delay(20000);
	}
}

void smoothTo2(int x, int y) {
	int currentX = lastX;
	int currentY = lastY;
	int steps = sqrtf(powf(currentX-x, 2) + powf(currentY-y,2)) / 5;
	int i;
	int dx = (x - currentX) / steps + 1;
	int dy = (y - currentY) / steps + 1;

	for (i = 1; i < steps+1; i++) {
		setPosition((int) (lastX + dx), (int) (lastY + dy));
		regularDelay();
	}
	if (lastX != x || lastY != y) {
		setPosition(x, y);
		regularDelay();
	}
}


int main1(void)
{
	WDTCTL = WDTPW + WDTHOLD;

	P1DIR |= BIT0; 							// Internal LEDs P1.0 of Launchpad is output

    P1DIR |= BIT6;							// P1.6/TA0.1 is used for PWM, thus also an output -> servo 1
    P2DIR |= BIT2;							// P2.2/TA1.1 is used for PWM, thus also an output -> servo 2
    P1DIR |= BIT7;




	P1OUT = 0; 								// Clear all outputs P1
	P2OUT = 0; 								// Clear all outputs P2

	 P1DIR &= ~BUTTON;                     // button is an input
	  P1OUT |= BUTTON;                      // pull-up resistor
	  P1REN |= BUTTON;                      // resistor enabled

  	P1SEL |= BIT6;                          // P1.6 select TA0.1 option
  	P2SEL |= BIT2;                          // P2.2 select TA1.1 option

	// if SMCLK is about 1MHz (or 1000000Hz),
	// and 1000ms are the equivalent of 1 Hz,
	// then, by setting CCR0 to 20000 (1000000 / 1000 * 20)
	// we get a period of 20ms
  	TA0CCR0 = 20000-1;                           // PWM Period TA0.1
  	TA1CCR0 = 20000-1;                           // PWM Period TA1.1

	TA0CCTL1 = OUTMOD_7;                       // CCR1 reset/set
	TA0CTL   = TASSEL_2 + MC_1;                // SMCLK, up mode
	TA1CCTL1 = OUTMOD_7;                       // CCR1 reset/set
	TA1CTL   = TASSEL_2 + MC_1;                // SMCLK, up mode

	init(700, 2300, 150);

	// loop just blinks build in LEDs to show activity
	for (;;)
	{
		smoothTo2(0, 200);
		smoothTo2(-100, 200);
		smoothTo2(0, 0);
	}
//
//	int last = P1IN & BUTTON;
//	int lastPos = 0;
//	while (1) {
//		if ((P1IN & BUTTON) != last) {
//			last = P1IN & BUTTON;
//			if (P1IN & BUTTON == 0) {
//				TA0CCTL1 = 0;
//			} else {
//				TA0CCTL1 = OUTMOD_7;                       // CCR1 reset/set
//				TA0CTL   = TASSEL_2 + MC_1;                // SMCLK, up mode
//				if (lastPos == 0) {
//					lastPos = 180;
//				} else {
//					lastPos = 0;
//				}
//				setPosition(lastPos);
//			}
//		}
//	}
}


