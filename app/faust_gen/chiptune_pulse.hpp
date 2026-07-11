/* ------------------------------------------------------------
name: "chiptune_pulse"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn ChiptunePulse -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __ChiptunePulse_H__
#define  __ChiptunePulse_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS ChiptunePulse
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

class ChiptunePulseSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec3[2];
	
  public:
	
	int getNumInputsChiptunePulseSIG0() {
		return 0;
	}
	int getNumOutputsChiptunePulseSIG0() {
		return 1;
	}
	
	void instanceInitChiptunePulseSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec3[l5] = 0;
		}
	}
	
	void fillChiptunePulseSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec3[0] = (iVec2[1] + iRec3[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec3[0]));
			iVec2[1] = iVec2[0];
			iRec3[1] = iRec3[0];
		}
	}

};

static ChiptunePulseSIG0* newChiptunePulseSIG0() { return (ChiptunePulseSIG0*)new ChiptunePulseSIG0(); }
static void deleteChiptunePulseSIG0(ChiptunePulseSIG0* dsp) { delete dsp; }

static float ftbl0ChiptunePulseSIG0[65536];

class ChiptunePulse : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec1[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec2[2];
	float fConst2;
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider0;
	float fConst5;
	float fRec4[2];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fRec6[2];
	FAUSTFLOAT fHslider4;
	int iRec7[2];
	FAUSTFLOAT fHslider5;
	FAUSTFLOAT fHslider6;
	FAUSTFLOAT fHslider7;
	float fRec5[2];
	FAUSTFLOAT fHslider8;
	float fVec3[2];
	FAUSTFLOAT fHslider9;
	float fConst6;
	float fRec0[2];
	
 public:
	ChiptunePulse() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn ChiptunePulse -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "chiptune_pulse.dsp");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "chiptune_pulse");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
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
		ChiptunePulseSIG0* sig0 = newChiptunePulseSIG0();
		sig0->instanceInitChiptunePulseSIG0(sample_rate);
		sig0->fillChiptunePulseSIG0(65536, ftbl0ChiptunePulseSIG0);
		deleteChiptunePulseSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 0.25f / std::max<float>(1.0f, 0.08f * fConst0);
		fConst5 = 1.0f / fConst0;
		fConst6 = 3.1415927f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(1.8f);
		fHslider1 = FAUSTFLOAT(0.12f);
		fHslider2 = FAUSTFLOAT(0.5f);
		fHslider3 = FAUSTFLOAT(5.0f);
		fHslider4 = FAUSTFLOAT(0.004f);
		fHslider5 = FAUSTFLOAT(0.04f);
		fHslider6 = FAUSTFLOAT(0.0f);
		fHslider7 = FAUSTFLOAT(2.2e+02f);
		fHslider8 = FAUSTFLOAT(0.7f);
		fHslider9 = FAUSTFLOAT(1.1e+04f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec6[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec7[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec5[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fVec3[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec0[l11] = 0.0f;
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
	
	virtual ChiptunePulse* clone() {
		return new ChiptunePulse();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("chiptune_pulse");
		ui_interface->addHorizontalSlider("drop", &fHslider6, FAUSTFLOAT(0.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("droptime", &fHslider5, FAUSTFLOAT(0.04f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("duty", &fHslider2, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.125f), FAUSTFLOAT(0.875f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider7, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider8, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("pwm", &fHslider1, FAUSTFLOAT(0.12f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("pwmrate", &fHslider0, FAUSTFLOAT(1.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tone", &fHslider9, FAUSTFLOAT(1.1e+04f), FAUSTFLOAT(8e+02f), FAUSTFLOAT(1.6e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("vibrate", &fHslider3, FAUSTFLOAT(5.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider4, FAUSTFLOAT(0.004f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.03f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = fConst5 * float(fHslider0);
		float fSlow3 = 0.5f * float(fHslider1);
		float fSlow4 = float(fHslider2);
		float fSlow5 = fConst5 * float(fHslider3);
		float fSlow6 = float(fHslider4);
		float fSlow7 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider5));
		float fSlow8 = float(fHslider6);
		float fSlow9 = fConst5 * float(fHslider7);
		float fSlow10 = 2.0f * float(fHslider8);
		float fSlow11 = 1.0f / std::tan(fConst6 * float(fHslider9));
		float fSlow12 = 1.0f - fSlow11;
		float fSlow13 = 1.0f / (fSlow11 + 1.0f);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec1[0] = iSlow1 * (iRec1[1] + 1);
			fRec2[0] = fSlow0 + fRec2[1] * float(fVec1[1] >= fSlow0);
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fSlow2 + fRec4[1]);
			fRec4[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = ((iTemp0) ? 0.0f : fSlow5 + fRec6[1]);
			fRec6[0] = fTemp2 - std::floor(fTemp2);
			iRec7[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec7[1] + (iRec7[1] > 0));
			float fTemp3 = float(iRec7[0]);
			float fTemp4 = ((iTemp0) ? 0.0f : fRec5[1] + fSlow9 * (fSlow8 * std::max<float>(0.0f, std::min<float>(fConst3 * fTemp3, fSlow7 * (fConst2 - fTemp3) + 1.0f)) + 1.0f) * (fSlow6 * ftbl0ChiptunePulseSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] + 1.0f));
			fRec5[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = fSlow10 * (float(fRec5[0] < (fSlow4 + fSlow3 * ftbl0ChiptunePulseSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))])) + -0.5f) * std::max<float>(0.0f, std::min<float>(fConst3 * fRec2[0], std::max<float>(fConst4 * (fConst2 - fRec2[0]) + 1.0f, 0.75f)) * (1.0f - fConst1 * float(iRec1[0])));
			fVec3[0] = fTemp5;
			fRec0[0] = -(fSlow13 * (fSlow12 * fRec0[1] - (fTemp5 + fVec3[1])));
			float fTemp6 = 0.912f * fRec0[0];
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			fRec4[1] = fRec4[0];
			fRec6[1] = fRec6[0];
			iRec7[1] = iRec7[0];
			fRec5[1] = fRec5[0];
			fVec3[1] = fVec3[0];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
