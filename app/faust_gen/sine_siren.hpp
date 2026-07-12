/* ------------------------------------------------------------
name: "sine_siren"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn SineSiren -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __SineSiren_H__
#define  __SineSiren_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS SineSiren
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

class SineSirenSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec3[2];
	
  public:
	
	int getNumInputsSineSirenSIG0() {
		return 0;
	}
	int getNumOutputsSineSirenSIG0() {
		return 1;
	}
	
	void instanceInitSineSirenSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec3[l5] = 0;
		}
	}
	
	void fillSineSirenSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec3[0] = (iVec2[1] + iRec3[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec3[0]));
			iVec2[1] = iVec2[0];
			iRec3[1] = iRec3[0];
		}
	}

};

static SineSirenSIG0* newSineSirenSIG0() { return (SineSirenSIG0*)new SineSirenSIG0(); }
static void deleteSineSirenSIG0(SineSirenSIG0* dsp) { delete dsp; }

static float ftbl0SineSirenSIG0[65536];

class SineSiren : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	float fConst2;
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider0;
	float fConst5;
	float fRec4[2];
	FAUSTFLOAT fHslider1;
	int iRec5[2];
	float fConst6;
	float fConst7;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	FAUSTFLOAT fHslider5;
	float fRec6[2];
	float fRec2[2];
	FAUSTFLOAT fHslider6;
	FAUSTFLOAT fHslider7;
	
 public:
	SineSiren() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn SineSiren -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "sine_siren.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "sine_siren");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		SineSirenSIG0* sig0 = newSineSirenSIG0();
		sig0->instanceInitSineSirenSIG0(sample_rate);
		sig0->fillSineSirenSIG0(65536, ftbl0SineSirenSIG0);
		deleteSineSirenSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.06f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 0.15f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst5 = 1.0f / fConst0;
		fConst6 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst7 = 1.0f / fConst6;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(5.5f);
		fHslider1 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(0.05f);
		fHslider3 = FAUSTFLOAT(0.35f);
		fHslider4 = FAUSTFLOAT(0.045f);
		fHslider5 = FAUSTFLOAT(2.2e+02f);
		fHslider6 = FAUSTFLOAT(0.12f);
		fHslider7 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iRec5[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec6[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
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
	
	virtual SineSiren* clone() {
		return new SineSiren();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("sine_siren");
		ui_interface->addHorizontalSlider("bite", &fHslider6, FAUSTFLOAT(0.12f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.6f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("drop", &fHslider3, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("droptime", &fHslider2, FAUSTFLOAT(0.05f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider5, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider7, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("glide", &fHslider4, FAUSTFLOAT(0.045f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("vibrate", &fHslider0, FAUSTFLOAT(5.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider1, FAUSTFLOAT(0.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.03f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = fConst5 * float(fHslider0);
		float fSlow3 = float(fHslider1);
		float fSlow4 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow5 = float(fHslider3);
		float fSlow6 = float(fHslider4);
		int iSlow7 = std::fabs(fSlow6) < 1.1920929e-07f;
		float fSlow8 = ((iSlow7) ? 0.0f : std::exp(-(fConst5 / ((iSlow7) ? 1.0f : fSlow6))));
		float fSlow9 = float(fHslider5) * (1.0f - fSlow8);
		float fSlow10 = float(fHslider6);
		float fSlow11 = 2.0f * fSlow10;
		float fSlow12 = 1.0f - fSlow10;
		float fSlow13 = 0.86f * float(fHslider7);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fSlow2 + fRec4[1]);
			fRec4[0] = fTemp1 - std::floor(fTemp1);
			iRec5[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec5[1] + (iRec5[1] > 0));
			float fTemp2 = float(iRec5[0]);
			fRec6[0] = fSlow9 + fSlow8 * fRec6[1];
			float fTemp3 = ((iTemp0) ? 0.0f : fRec2[1] + fConst5 * fRec6[0] * (fSlow5 * std::max<float>(0.0f, std::min<float>(fConst7 * fTemp2, fSlow4 * (fConst6 - fTemp2) + 1.0f)) + 1.0f) * (fSlow3 * ftbl0SineSirenSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] + 1.0f));
			fRec2[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = fSlow13 * (fSlow12 * ftbl0SineSirenSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec2[0]), 65535))] + fSlow11 * (float(fRec2[0] < 0.5f) + -0.5f)) * std::max<float>(0.0f, std::min<float>(fConst3 * fRec1[0], std::max<float>(fConst4 * (fConst2 - fRec1[0]) + 1.0f, 0.85f)) * (1.0f - fConst1 * float(iRec0[0])));
			output0[i0] = FAUSTFLOAT(fTemp4);
			output1[i0] = FAUSTFLOAT(fTemp4);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec4[1] = fRec4[0];
			iRec5[1] = iRec5[0];
			fRec6[1] = fRec6[0];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
