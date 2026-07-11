/* ------------------------------------------------------------
name: "fx_softclip"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxSoftclip -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxSoftclip_H__
#define  __FxSoftclip_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxSoftclip
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif


class FxSoftclip : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fHslider0;
	float fRec0[2];
	int IOTA0;
	float fVec0[32];
	float fVec1[32];
	float fVec2[32];
	float fVec3[2];
	float fVec4[32];
	float fVec5[32];
	float fVec6[32];
	float fVec7[2];
	
 public:
	FxSoftclip() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxSoftclip -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_softclip.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_softclip");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = 44.1f / std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f - fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(3.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fRec0[l0] = 0.0f;
		}
		IOTA0 = 0;
		for (int l1 = 0; l1 < 32; l1 = l1 + 1) {
			fVec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 32; l2 = l2 + 1) {
			fVec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 32; l3 = l3 + 1) {
			fVec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fVec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 32; l5 = l5 + 1) {
			fVec4[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 32; l6 = l6 + 1) {
			fVec5[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 32; l7 = l7 + 1) {
			fVec6[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fVec7[l8] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual FxSoftclip* clone() {
		return new FxSoftclip();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_softclip");
		ui_interface->addHorizontalSlider("drive", &fHslider0, FAUSTFLOAT(3.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst0 * std::pow(1e+01f, 0.05f * float(fHslider0));
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fRec0[0] = fSlow0 + fConst1 * fRec0[1];
			float fTemp0 = float(input0[i0]);
			fVec0[IOTA0 & 31] = fTemp0;
			float fTemp1 = fVec0[(IOTA0 - 1) & 31];
			float fTemp2 = fVec0[(IOTA0 - 30) & 31];
			float fTemp3 = fVec0[(IOTA0 - 12) & 31];
			float fTemp4 = fVec0[(IOTA0 - 19) & 31];
			float fTemp5 = fVec0[(IOTA0 - 14) & 31];
			float fTemp6 = fVec0[(IOTA0 - 17) & 31];
			float fTemp7 = fVec0[(IOTA0 - 10) & 31];
			float fTemp8 = fVec0[(IOTA0 - 21) & 31];
			float fTemp9 = fVec0[(IOTA0 - 9) & 31];
			float fTemp10 = fVec0[(IOTA0 - 22) & 31];
			float fTemp11 = fVec0[(IOTA0 - 7) & 31];
			float fTemp12 = fVec0[(IOTA0 - 24) & 31];
			float fTemp13 = fVec0[(IOTA0 - 5) & 31];
			float fTemp14 = fVec0[(IOTA0 - 26) & 31];
			float fTemp15 = fVec0[(IOTA0 - 3) & 31];
			float fTemp16 = fVec0[(IOTA0 - 28) & 31];
			float fTemp17 = fVec0[(IOTA0 - 13) & 31];
			float fTemp18 = fVec0[(IOTA0 - 18) & 31];
			float fTemp19 = fVec0[(IOTA0 - 15) & 31];
			float fTemp20 = fVec0[(IOTA0 - 16) & 31];
			float fTemp21 = fVec0[(IOTA0 - 11) & 31];
			float fTemp22 = fVec0[(IOTA0 - 20) & 31];
			float fTemp23 = fVec0[(IOTA0 - 8) & 31];
			float fTemp24 = fVec0[(IOTA0 - 23) & 31];
			float fTemp25 = fVec0[(IOTA0 - 6) & 31];
			float fTemp26 = fVec0[(IOTA0 - 25) & 31];
			float fTemp27 = fVec0[(IOTA0 - 4) & 31];
			float fTemp28 = fVec0[(IOTA0 - 27) & 31];
			float fTemp29 = fVec0[(IOTA0 - 2) & 31];
			float fTemp30 = fVec0[(IOTA0 - 29) & 31];
			float fTemp31 = tanhf(fRec0[0] * (0.0014493224f * (fTemp0 + fVec0[(IOTA0 - 31) & 31]) + 0.0040928987f * (fTemp30 + fTemp29) + 0.00863951f * (fTemp28 + fTemp27) + 0.012050141f * (fTemp26 + fTemp25) + 0.00927321f * (fTemp24 + fTemp23) + 0.024531988f * (fTemp22 + fTemp21) + 0.6301972f * (fTemp20 + fTemp19) + 0.09729849f * (fTemp18 + fTemp17) - (0.0063390755f * (fTemp16 + fTemp15) + 0.01074012f * (fTemp14 + fTemp13) + 0.011850124f * (fTemp12 + fTemp11) + 0.003293757f * (fTemp10 + fTemp9) + 0.007361487f * (fTemp8 + fTemp7) + 0.19336526f * (fTemp6 + fTemp5) + 0.05164404f * (fTemp4 + fTemp3) + 0.0029389453f * (fTemp2 + fTemp1)))) / fRec0[0];
			fVec1[IOTA0 & 31] = fTemp31;
			float fTemp32 = tanhf(fRec0[0] * (0.0013272606f * (fTemp30 + fTemp1) + 0.0032839319f * (fTemp14 + fTemp27) + 0.013509034f * (fTemp12 + fTemp25) + 0.03001481f * (fTemp10 + fTemp23) + 0.050180957f * (fTemp22 + fTemp7) + 0.068803534f * (fTemp18 + fTemp3) + 0.91845846f * fTemp19 + 0.080039404f * (fTemp20 + fTemp5) - (0.0010161299f * (fTemp16 + fTemp29) + 0.0005279349f * (fTemp28 + fTemp15) + 0.007569385f * (fTemp26 + fTemp13) + 0.021067325f * (fTemp24 + fTemp11) + 0.039921504f * (fTemp8 + fTemp9) + 0.0756591f * (fTemp6 + fTemp17) + 0.060066942f * (fTemp4 + fTemp21) + 0.002636371f * (fTemp0 + fTemp2)))) / fRec0[0];
			fVec2[IOTA0 & 31] = fTemp32;
			fVec3[0] = 0.0006636303f * (fVec2[(IOTA0 - 1) & 31] + fVec2[(IOTA0 - 29) & 31]) + 0.001641966f * (fVec2[(IOTA0 - 4) & 31] + fVec2[(IOTA0 - 26) & 31]) + 0.006754517f * (fVec2[(IOTA0 - 6) & 31] + fVec2[(IOTA0 - 24) & 31]) + 0.015007406f * (fVec2[(IOTA0 - 8) & 31] + fVec2[(IOTA0 - 22) & 31]) + 0.025090478f * (fVec2[(IOTA0 - 10) & 31] + fVec2[(IOTA0 - 20) & 31]) + 0.034401767f * (fVec2[(IOTA0 - 12) & 31] + fVec2[(IOTA0 - 18) & 31]) + 0.45922923f * fVec2[(IOTA0 - 15) & 31] + 0.040019702f * (fVec2[(IOTA0 - 14) & 31] + fVec2[(IOTA0 - 16) & 31]) - (0.0005080649f * (fVec2[(IOTA0 - 2) & 31] + fVec2[(IOTA0 - 28) & 31]) + 0.0002639674f * (fVec2[(IOTA0 - 3) & 31] + fVec2[(IOTA0 - 27) & 31]) + 0.0037846926f * (fVec2[(IOTA0 - 5) & 31] + fVec2[(IOTA0 - 25) & 31]) + 0.0105336625f * (fVec2[(IOTA0 - 7) & 31] + fVec2[(IOTA0 - 23) & 31]) + 0.019960752f * (fVec2[(IOTA0 - 9) & 31] + fVec2[(IOTA0 - 21) & 31]) + 0.03782955f * (fVec2[(IOTA0 - 13) & 31] + fVec2[(IOTA0 - 17) & 31]) + 0.030033471f * (fVec2[(IOTA0 - 11) & 31] + fVec2[(IOTA0 - 19) & 31]) + 0.0013181855f * (fTemp32 + fVec2[(IOTA0 - 30) & 31]));
			output0[i0] = FAUSTFLOAT(0.0007246612f * (fTemp31 + fVec1[(IOTA0 - 31) & 31]) + 0.0020464493f * (fVec1[(IOTA0 - 2) & 31] + fVec1[(IOTA0 - 29) & 31]) + 0.004319755f * (fVec1[(IOTA0 - 4) & 31] + fVec1[(IOTA0 - 27) & 31]) + 0.0060250703f * (fVec1[(IOTA0 - 6) & 31] + fVec1[(IOTA0 - 25) & 31]) + 0.004636605f * (fVec1[(IOTA0 - 8) & 31] + fVec1[(IOTA0 - 23) & 31]) + 0.012265995f * (fVec1[(IOTA0 - 11) & 31] + fVec1[(IOTA0 - 20) & 31]) + 0.3150986f * (fVec1[(IOTA0 - 15) & 31] + fVec1[(IOTA0 - 16) & 31]) + 0.048649244f * (fVec1[(IOTA0 - 13) & 31] + fVec1[(IOTA0 - 18) & 31]) + fVec3[1] - (0.0031695378f * (fVec1[(IOTA0 - 3) & 31] + fVec1[(IOTA0 - 28) & 31]) + 0.0053700595f * (fVec1[(IOTA0 - 5) & 31] + fVec1[(IOTA0 - 26) & 31]) + 0.005925062f * (fVec1[(IOTA0 - 7) & 31] + fVec1[(IOTA0 - 24) & 31]) + 0.0016468785f * (fVec1[(IOTA0 - 9) & 31] + fVec1[(IOTA0 - 22) & 31]) + 0.02582202f * (fVec1[(IOTA0 - 12) & 31] + fVec1[(IOTA0 - 19) & 31]) + 0.09668263f * (fVec1[(IOTA0 - 14) & 31] + fVec1[(IOTA0 - 17) & 31]) + 0.0036807435f * (fVec1[(IOTA0 - 10) & 31] + fVec1[(IOTA0 - 21) & 31]) + 0.0014694727f * (fVec1[(IOTA0 - 1) & 31] + fVec1[(IOTA0 - 30) & 31])));
			float fTemp33 = float(input1[i0]);
			fVec4[IOTA0 & 31] = fTemp33;
			float fTemp34 = fVec4[(IOTA0 - 1) & 31];
			float fTemp35 = fVec4[(IOTA0 - 30) & 31];
			float fTemp36 = fVec4[(IOTA0 - 12) & 31];
			float fTemp37 = fVec4[(IOTA0 - 19) & 31];
			float fTemp38 = fVec4[(IOTA0 - 14) & 31];
			float fTemp39 = fVec4[(IOTA0 - 17) & 31];
			float fTemp40 = fVec4[(IOTA0 - 10) & 31];
			float fTemp41 = fVec4[(IOTA0 - 21) & 31];
			float fTemp42 = fVec4[(IOTA0 - 9) & 31];
			float fTemp43 = fVec4[(IOTA0 - 22) & 31];
			float fTemp44 = fVec4[(IOTA0 - 7) & 31];
			float fTemp45 = fVec4[(IOTA0 - 24) & 31];
			float fTemp46 = fVec4[(IOTA0 - 5) & 31];
			float fTemp47 = fVec4[(IOTA0 - 26) & 31];
			float fTemp48 = fVec4[(IOTA0 - 3) & 31];
			float fTemp49 = fVec4[(IOTA0 - 28) & 31];
			float fTemp50 = fVec4[(IOTA0 - 13) & 31];
			float fTemp51 = fVec4[(IOTA0 - 18) & 31];
			float fTemp52 = fVec4[(IOTA0 - 15) & 31];
			float fTemp53 = fVec4[(IOTA0 - 16) & 31];
			float fTemp54 = fVec4[(IOTA0 - 11) & 31];
			float fTemp55 = fVec4[(IOTA0 - 20) & 31];
			float fTemp56 = fVec4[(IOTA0 - 8) & 31];
			float fTemp57 = fVec4[(IOTA0 - 23) & 31];
			float fTemp58 = fVec4[(IOTA0 - 6) & 31];
			float fTemp59 = fVec4[(IOTA0 - 25) & 31];
			float fTemp60 = fVec4[(IOTA0 - 4) & 31];
			float fTemp61 = fVec4[(IOTA0 - 27) & 31];
			float fTemp62 = fVec4[(IOTA0 - 2) & 31];
			float fTemp63 = fVec4[(IOTA0 - 29) & 31];
			float fTemp64 = tanhf(fRec0[0] * (0.0014493224f * (fTemp33 + fVec4[(IOTA0 - 31) & 31]) + 0.0040928987f * (fTemp63 + fTemp62) + 0.00863951f * (fTemp61 + fTemp60) + 0.012050141f * (fTemp59 + fTemp58) + 0.00927321f * (fTemp57 + fTemp56) + 0.024531988f * (fTemp55 + fTemp54) + 0.6301972f * (fTemp53 + fTemp52) + 0.09729849f * (fTemp51 + fTemp50) - (0.0063390755f * (fTemp49 + fTemp48) + 0.01074012f * (fTemp47 + fTemp46) + 0.011850124f * (fTemp45 + fTemp44) + 0.003293757f * (fTemp43 + fTemp42) + 0.007361487f * (fTemp41 + fTemp40) + 0.19336526f * (fTemp39 + fTemp38) + 0.05164404f * (fTemp37 + fTemp36) + 0.0029389453f * (fTemp35 + fTemp34)))) / fRec0[0];
			fVec5[IOTA0 & 31] = fTemp64;
			float fTemp65 = tanhf(fRec0[0] * (0.0013272606f * (fTemp63 + fTemp34) + 0.0032839319f * (fTemp47 + fTemp60) + 0.013509034f * (fTemp45 + fTemp58) + 0.03001481f * (fTemp43 + fTemp56) + 0.050180957f * (fTemp55 + fTemp40) + 0.068803534f * (fTemp51 + fTemp36) + 0.91845846f * fTemp52 + 0.080039404f * (fTemp53 + fTemp38) - (0.0010161299f * (fTemp49 + fTemp62) + 0.0005279349f * (fTemp61 + fTemp48) + 0.007569385f * (fTemp59 + fTemp46) + 0.021067325f * (fTemp57 + fTemp44) + 0.039921504f * (fTemp41 + fTemp42) + 0.0756591f * (fTemp39 + fTemp50) + 0.060066942f * (fTemp37 + fTemp54) + 0.002636371f * (fTemp33 + fTemp35)))) / fRec0[0];
			fVec6[IOTA0 & 31] = fTemp65;
			fVec7[0] = 0.0006636303f * (fVec6[(IOTA0 - 1) & 31] + fVec6[(IOTA0 - 29) & 31]) + 0.001641966f * (fVec6[(IOTA0 - 4) & 31] + fVec6[(IOTA0 - 26) & 31]) + 0.015007406f * (fVec6[(IOTA0 - 8) & 31] + fVec6[(IOTA0 - 22) & 31]) + 0.006754517f * (fVec6[(IOTA0 - 6) & 31] + fVec6[(IOTA0 - 24) & 31]) + 0.025090478f * (fVec6[(IOTA0 - 10) & 31] + fVec6[(IOTA0 - 20) & 31]) + 0.034401767f * (fVec6[(IOTA0 - 12) & 31] + fVec6[(IOTA0 - 18) & 31]) + 0.45922923f * fVec6[(IOTA0 - 15) & 31] + 0.040019702f * (fVec6[(IOTA0 - 14) & 31] + fVec6[(IOTA0 - 16) & 31]) - (0.0005080649f * (fVec6[(IOTA0 - 2) & 31] + fVec6[(IOTA0 - 28) & 31]) + 0.0002639674f * (fVec6[(IOTA0 - 3) & 31] + fVec6[(IOTA0 - 27) & 31]) + 0.0037846926f * (fVec6[(IOTA0 - 5) & 31] + fVec6[(IOTA0 - 25) & 31]) + 0.0105336625f * (fVec6[(IOTA0 - 7) & 31] + fVec6[(IOTA0 - 23) & 31]) + 0.019960752f * (fVec6[(IOTA0 - 9) & 31] + fVec6[(IOTA0 - 21) & 31]) + 0.03782955f * (fVec6[(IOTA0 - 13) & 31] + fVec6[(IOTA0 - 17) & 31]) + 0.030033471f * (fVec6[(IOTA0 - 11) & 31] + fVec6[(IOTA0 - 19) & 31]) + 0.0013181855f * (fTemp65 + fVec6[(IOTA0 - 30) & 31]));
			output1[i0] = FAUSTFLOAT(0.0007246612f * (fTemp64 + fVec5[(IOTA0 - 31) & 31]) + 0.0020464493f * (fVec5[(IOTA0 - 2) & 31] + fVec5[(IOTA0 - 29) & 31]) + 0.0060250703f * (fVec5[(IOTA0 - 6) & 31] + fVec5[(IOTA0 - 25) & 31]) + 0.004319755f * (fVec5[(IOTA0 - 4) & 31] + fVec5[(IOTA0 - 27) & 31]) + 0.004636605f * (fVec5[(IOTA0 - 8) & 31] + fVec5[(IOTA0 - 23) & 31]) + 0.012265995f * (fVec5[(IOTA0 - 11) & 31] + fVec5[(IOTA0 - 20) & 31]) + 0.3150986f * (fVec5[(IOTA0 - 15) & 31] + fVec5[(IOTA0 - 16) & 31]) + 0.048649244f * (fVec5[(IOTA0 - 13) & 31] + fVec5[(IOTA0 - 18) & 31]) + fVec7[1] - (0.0031695378f * (fVec5[(IOTA0 - 3) & 31] + fVec5[(IOTA0 - 28) & 31]) + 0.0053700595f * (fVec5[(IOTA0 - 5) & 31] + fVec5[(IOTA0 - 26) & 31]) + 0.005925062f * (fVec5[(IOTA0 - 7) & 31] + fVec5[(IOTA0 - 24) & 31]) + 0.0016468785f * (fVec5[(IOTA0 - 9) & 31] + fVec5[(IOTA0 - 22) & 31]) + 0.0036807435f * (fVec5[(IOTA0 - 10) & 31] + fVec5[(IOTA0 - 21) & 31]) + 0.09668263f * (fVec5[(IOTA0 - 14) & 31] + fVec5[(IOTA0 - 17) & 31]) + 0.02582202f * (fVec5[(IOTA0 - 12) & 31] + fVec5[(IOTA0 - 19) & 31]) + 0.0014694727f * (fVec5[(IOTA0 - 1) & 31] + fVec5[(IOTA0 - 30) & 31])));
			fRec0[1] = fRec0[0];
			IOTA0 = IOTA0 + 1;
			fVec3[1] = fVec3[0];
			fVec7[1] = fVec7[0];
		}
	}

};

#endif
