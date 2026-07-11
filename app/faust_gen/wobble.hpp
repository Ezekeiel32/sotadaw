/* ------------------------------------------------------------
name: "wobble"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Wobble -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Wobble_H__
#define  __Wobble_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Wobble
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

class WobbleSIG0 {
	
  private:
	
	int iVec0[2];
	int iRec0[2];
	
  public:
	
	int getNumInputsWobbleSIG0() {
		return 0;
	}
	int getNumOutputsWobbleSIG0() {
		return 1;
	}
	
	void instanceInitWobbleSIG0(int sample_rate) {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
	}
	
	void fillWobbleSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec0[0] = 1;
			iRec0[0] = (iVec0[1] + iRec0[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec0[0]));
			iVec0[1] = iVec0[0];
			iRec0[1] = iRec0[0];
		}
	}

};

static WobbleSIG0* newWobbleSIG0() { return (WobbleSIG0*)new WobbleSIG0(); }
static void deleteWobbleSIG0(WobbleSIG0* dsp) { delete dsp; }

static float ftbl0WobbleSIG0[65536];
static float Wobble_faustpower2_f(float value) {
	return value * value;
}

class Wobble : public dsp {
	
 private:
	
	int iVec1[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst2;
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fButton0;
	float fVec2[2];
	int iRec3[2];
	float fConst4;
	float fRec4[2];
	float fConst5;
	float fConst6;
	float fConst7;
	FAUSTFLOAT fHslider4;
	float fRec5[2];
	float fRec7[2];
	FAUSTFLOAT fHslider5;
	float fRec2[3];
	
 public:
	Wobble() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Wobble -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "wobble.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "wobble");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		WobbleSIG0* sig0 = newWobbleSIG0();
		sig0->instanceInitWobbleSIG0(sample_rate);
		sig0->fillWobbleSIG0(65536, ftbl0WobbleSIG0);
		deleteWobbleSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / fConst0;
		fConst2 = 3.1415927f / fConst0;
		float fConst3 = std::max<float>(1.0f, 0.2f * fConst0);
		fConst4 = 1.0f / fConst3;
		fConst5 = std::max<float>(1.0f, 0.01f * fConst0);
		fConst6 = 1.0f / fConst5;
		fConst7 = 0.1f / fConst3;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(4.0f);
		fHslider1 = FAUSTFLOAT(4e+03f);
		fHslider2 = FAUSTFLOAT(2e+02f);
		fHslider3 = FAUSTFLOAT(6.0f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider4 = FAUSTFLOAT(55.0f);
		fHslider5 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iVec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fVec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec3[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec5[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec2[l9] = 0.0f;
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
	
	virtual Wobble* clone() {
		return new Wobble();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("wobble");
		ui_interface->addHorizontalSlider("base", &fHslider2, FAUSTFLOAT(2e+02f), FAUSTFLOAT(5e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("depth", &fHslider1, FAUSTFLOAT(4e+03f), FAUSTFLOAT(2e+02f), FAUSTFLOAT(8e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(55.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("rate", &fHslider0, FAUSTFLOAT(4.0f), FAUSTFLOAT(0.1f), FAUSTFLOAT(16.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("res", &fHslider3, FAUSTFLOAT(6.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst1 * float(fHslider0);
		float fSlow1 = 0.5f * float(fHslider1);
		float fSlow2 = float(fHslider2);
		float fSlow3 = 1.0f / float(fHslider3);
		float fSlow4 = float(fButton0);
		int iSlow5 = fSlow4 == 0.0f;
		float fSlow6 = float(fHslider4);
		float fSlow7 = std::max<float>(1.1920929e-07f, std::fabs(1.01f * fSlow6));
		float fSlow8 = fConst1 * fSlow7;
		float fSlow9 = 1.0f - fConst0 / fSlow7;
		float fSlow10 = std::max<float>(1.1920929e-07f, std::fabs(fSlow6));
		float fSlow11 = fConst1 * fSlow10;
		float fSlow12 = 1.0f - fConst0 / fSlow10;
		float fSlow13 = float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec1[0] = 1;
			float fTemp0 = ((1 - iVec1[1]) ? 0.0f : fSlow0 + fRec1[1]);
			fRec1[0] = fTemp0 - std::floor(fTemp0);
			float fTemp1 = std::tan(fConst2 * (fSlow2 + fSlow1 * (ftbl0WobbleSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec1[0]), 65535))] + 1.0f)));
			float fTemp2 = 1.0f / fTemp1;
			float fTemp3 = (fSlow3 + fTemp2) / fTemp1 + 1.0f;
			fVec2[0] = fSlow4;
			iRec3[0] = iSlow5 * (iRec3[1] + 1);
			fRec4[0] = fSlow4 + fRec4[1] * float(fVec2[1] >= fSlow4);
			float fTemp4 = fSlow8 + fRec5[1] + -1.0f;
			int iTemp5 = fTemp4 < 0.0f;
			float fTemp6 = fSlow8 + fRec5[1];
			fRec5[0] = ((iTemp5) ? fTemp6 : fTemp4);
			float fRec6 = ((iTemp5) ? fTemp6 : fSlow8 + fRec5[1] + fSlow9 * fTemp4);
			float fTemp7 = fSlow11 + fRec7[1] + -1.0f;
			int iTemp8 = fTemp7 < 0.0f;
			float fTemp9 = fSlow11 + fRec7[1];
			fRec7[0] = ((iTemp8) ? fTemp9 : fTemp7);
			float fRec8 = ((iTemp8) ? fTemp9 : fSlow11 + fRec7[1] + fSlow12 * fTemp7);
			fRec2[0] = -(fSlow13 * (1.0f - (fRec8 + fRec6)) * std::max<float>(0.0f, std::min<float>(fConst6 * fRec4[0], std::max<float>(fConst7 * (fConst5 - fRec4[0]) + 1.0f, 0.9f)) * (1.0f - fConst4 * float(iRec3[0]))) + (fRec2[2] * ((fTemp2 - fSlow3) / fTemp1 + 1.0f) + 2.0f * fRec2[1] * (1.0f - 1.0f / Wobble_faustpower2_f(fTemp1))) / fTemp3);
			float fTemp10 = 0.2598f * ((fRec2[2] + fRec2[0] + 2.0f * fRec2[1]) / fTemp3);
			output0[i0] = FAUSTFLOAT(fTemp10);
			output1[i0] = FAUSTFLOAT(fTemp10);
			iVec1[1] = iVec1[0];
			fRec1[1] = fRec1[0];
			fVec2[1] = fVec2[0];
			iRec3[1] = iRec3[0];
			fRec4[1] = fRec4[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
