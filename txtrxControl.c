#include <msp430.h>

#define TXLED BIT0
#define RXLED BIT0
#define TXD BIT2
#define RXD BIT1


const char string[] = { "He\r\n" };
unsigned int i; //Counter

void delay()
{
	P1OUT ^= BIT0;
	volatile unsigned long j;
	j = 49999;
	do (j--);
	while (j != 0);
}

int main(void)
{
	WDTCTL = WDTPW + WDTHOLD;

	//DCOCTL = 0; // Select lowest DCOx and MODx settings
	BCSCTL1 = CALBC1_1MHZ; // Set DCO
	DCOCTL = CALDCO_1MHZ;

	P1DIR |= BIT0; 							// Internal LEDs P1.0 of Launchpad is output

    P1DIR |= BIT6;							// P1.6/TA0.1 is used for PWM, thus also an output -> servo 1
    P2DIR |= 0xFF;							// P2.2/TA1.1 is used for PWM, thus also an output -> servo 2

  	P1SEL |= BIT6;                          // P1.6 select TA0.1 option
  	P2SEL |= BIT2;                          // P2.2 select TA1.1 option

	P1OUT = 0; 								// Clear all outputs P1
	P2OUT = 0; 								// Clear all outputs P2

	P1SEL |= RXD + TXD ; // P1.1 = RXD, P1.2=TXD
	P1SEL2 |= RXD + TXD ; // P1.1 = RXD, P1.2=TXD
	P1DIR |= RXLED + TXLED;
	P1OUT &= 0x00;



	// if SMCLK is about 1MHz (or 1000000Hz),
	// and 1000ms are the equivalent of 1 Hz,
	// then, by setting CCR0 to 20000 (1000000 / 1000 * 20)
	// we get a period of 20ms
  	TA0CCR0 = 20000-1;                           // PWM Period TA0.1
  	TA1CCR0 = 20000-1;                           // PWM Period TA1.1

	TA0CCR1 = 800;
	TA1CCR1 = 1500;

	TA0CCTL1 = OUTMOD_7;                       // CCR1 reset/set
	TA0CTL   = TASSEL_2 + MC_1;                // SMCLK, up mode
	TA1CCTL1 = OUTMOD_7;                       // CCR1 reset/set
	TA1CTL   = TASSEL_2 + MC_1;                // SMCLK, up mode



	UCA0CTL1 |= UCSSEL_2; // SMCLK
	UCA0BR0 = 0x08; // 1MHz 115200
	UCA0BR1 = 0x00; // 1MHz 115200
	UCA0MCTL = UCBRS2 + UCBRS0; // Modulation UCBRSx = 5
	UCA0CTL1 &= ~UCSWRST; // **Initialize USCI state machine**
	UC0IE |= UCA0RXIE; // Enable USCI_A0 RX interrupt
	__bis_SR_register(LPM0_bits + GIE); // Enter LPM0 w/ int until Byte RXed



	// loop just blinks build in LEDs to show activity
	for (;;)
	{

	}
}

#pragma vector=USCIAB0TX_VECTOR
__interrupt void USCI0TX_ISR(void)
{
	P1OUT |= TXLED;
	UCA0TXBUF = string[i++]; // TX next character
	if (i == sizeof string - 1) { // TX over?
		UC0IE &= ~UCA0TXIE; // Disable USCI_A0 TX interrupt
	}
	P1OUT &= ~TXLED;
}

//126 = startByte
//127 = stopByte

unsigned volatile int xValue = 1500;
unsigned volatile int yValue = 1500;
unsigned volatile int step = 0;

#pragma vector=USCIAB0RX_VECTOR
__interrupt void USCI0RX_ISR(void)
{
   P1OUT |= RXLED;
   if (UCA0RXBUF == 126) {
	   xValue = 0;
	   yValue = 0;
	   step = 1;
   } else if (UCA0RXBUF == 127) {
	   if (xValue < 700 || xValue > 2300) {
		   xValue = 1500;
	   }
	   if (yValue < 700 || yValue > 2300) {
			yValue = 1500;
	   }
	   TA0CCR1 = xValue;
	   TA1CCR1 = yValue;
	   step = 0;
   } else {
		switch(step++) {
			case 1:
				xValue = UCA0RXBUF * 100;
				break;
			case 2:
				xValue += UCA0RXBUF;
				break;
			case 3:
				yValue = UCA0RXBUF * 100;
				break;
			case 4:
				yValue += UCA0RXBUF ;
				break;
			default:
				break;
		}
   }
   P1OUT &= ~RXLED;

//    if (UCA0RXBUF == 'a') {// 'a' received?
//       i = 0;
//       UC0IE |= UCA0TXIE; // Enable USCI_A0 TX interrupt
//      UCA0TXBUF = string[i++];
//    }
//    P1OUT &= ~RXLED;
}
