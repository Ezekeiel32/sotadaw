/* ------------------------------------------------------------
name: "rhodes"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Rhodes -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Rhodes_H__
#define  __Rhodes_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Rhodes
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

class RhodesSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsRhodesSIG0() {
		return 0;
	}
	int getNumOutputsRhodesSIG0() {
		return 1;
	}
	
	void instanceInitRhodesSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec2[l5] = 0;
		}
	}
	
	void fillRhodesSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec2[0] = (iVec2[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec2[1] = iVec2[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static RhodesSIG0* newRhodesSIG0() { return (RhodesSIG0*)new RhodesSIG0(); }
static void deleteRhodesSIG0(RhodesSIG0* dsp) { delete dsp; }

static float ftbl0RhodesSIG0[65536];

class Rhodes : public dsp {
	
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
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	int iRec4[2];
	float fConst4;
	float fConst5;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fConst6;
	float fRec5[2];
	FAUSTFLOAT fHslider4;
	float fConst7;
	float fRec3[2];
	FAUSTFLOAT fHslider5;
	
 public:
	Rhodes() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Rhodes -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "rhodes.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "rhodes");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
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
		RhodesSIG0* sig0 = newRhodesSIG0();
		sig0->instanceInitRhodesSIG0(sample_rate);
		sig0->fillRhodesSIG0(65536, ftbl0RhodesSIG0);
		deleteRhodesSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.4f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.005f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst5 = 1.0f / fConst4;
		fConst6 = 2.0f / fConst0;
		fConst7 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(1.2f);
		fHslider1 = FAUSTFLOAT(0.3f);
		fHslider2 = FAUSTFLOAT(0.4f);
		fHslider3 = FAUSTFLOAT(2.2e+02f);
		fHslider4 = FAUSTFLOAT(1.2f);
		fHslider5 = FAUSTFLOAT(0.6f);
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
			iRec4[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec5[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec3[l8] = 0.0f;
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
	
	virtual Rhodes* clone() {
		return new Rhodes();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("rhodes");
		ui_interface->addHorizontalSlider("bark", &fHslider2, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.05f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("bell", &fHslider4, FAUSTFLOAT(1.2f), FAUSTFLOAT(0.0f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(1.2f), FAUSTFLOAT(0.4f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sustain", &fHslider1, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.8f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = float(fHslider1);
		float fSlow3 = (1.0f - fSlow2) / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow4 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow5 = float(fHslider3);
		float fSlow6 = fConst6 * fSlow5;
		float fSlow7 = 2.0f * float(fHslider4);
		float fSlow8 = fConst7 * fSlow5;
		float fSlow9 = 0.913f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			int iTemp0 = 1 - iVec0[1];
			iRec4[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec4[1] + (iRec4[1] > 0));
			float fTemp1 = float(iRec4[0]);
			float fTemp2 = ((iTemp0) ? 0.0f : fSlow6 + fRec5[1]);
			fRec5[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = ((iTemp0) ? 0.0f : fRec3[1] + fSlow8 * (fSlow7 * ftbl0RhodesSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec5[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst5 * fTemp1, fSlow4 * (fConst4 - fTemp1) + 1.0f)) + 1.0f));
			fRec3[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = fSlow9 * ftbl0RhodesSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst3 * fRec1[0], std::max<float>(fSlow3 * (fConst2 - fRec1[0]) + 1.0f, fSlow2)) * (1.0f - fConst1 * float(iRec0[0])));
			output0[i0] = FAUSTFLOAT(fTemp4);
			output1[i0] = FAUSTFLOAT(fTemp4);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			iRec4[1] = iRec4[0];
			fRec5[1] = fRec5[0];
			fRec3[1] = fRec3[0];
		}
	}

};

#endif
