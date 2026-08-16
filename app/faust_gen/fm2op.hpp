/* ------------------------------------------------------------
name: "fm2op"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Fm2op -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Fm2op_H__
#define  __Fm2op_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Fm2op
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

class Fm2opSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsFm2opSIG0() {
		return 0;
	}
	int getNumOutputsFm2opSIG0() {
		return 1;
	}
	
	void instanceInitFm2opSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec2[l5] = 0;
		}
	}
	
	void fillFm2opSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec2[0] = (iVec2[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec2[1] = iVec2[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static Fm2opSIG0* newFm2opSIG0() { return (Fm2opSIG0*)new Fm2opSIG0(); }
static void deleteFm2opSIG0(Fm2opSIG0* dsp) { delete dsp; }

class Fm2opSIG1 {
	
  private:
	
	int iVec3[2];
	int iRec4[2];
	
  public:
	
	int getNumInputsFm2opSIG1() {
		return 0;
	}
	int getNumOutputsFm2opSIG1() {
		return 1;
	}
	
	void instanceInitFm2opSIG1(int sample_rate) {
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iVec3[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec4[l8] = 0;
		}
	}
	
	void fillFm2opSIG1(int count, float* table) {
		for (int i2 = 0; i2 < count; i2 = i2 + 1) {
			iVec3[0] = 1;
			iRec4[0] = (iVec3[1] + iRec4[1]) % 65536;
			table[i2] = std::cos(9.58738e-05f * float(iRec4[0]));
			iVec3[1] = iVec3[0];
			iRec4[1] = iRec4[0];
		}
	}

};

static Fm2opSIG1* newFm2opSIG1() { return (Fm2opSIG1*)new Fm2opSIG1(); }
static void deleteFm2opSIG1(Fm2opSIG1* dsp) { delete dsp; }

static float ftbl0Fm2opSIG0[65536];
static float ftbl1Fm2opSIG1[65536];

class Fm2op : public dsp {
	
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
	FAUSTFLOAT fHslider2;
	float fConst4;
	float fConst5;
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fConst6;
	float fRec3[2];
	FAUSTFLOAT fHslider5;
	float fRec5[2];
	FAUSTFLOAT fHslider6;
	
 public:
	Fm2op() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Fm2op -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "fm2op.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fm2op");
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
		Fm2opSIG0* sig0 = newFm2opSIG0();
		sig0->instanceInitFm2opSIG0(sample_rate);
		sig0->fillFm2opSIG0(65536, ftbl0Fm2opSIG0);
		Fm2opSIG1* sig1 = newFm2opSIG1();
		sig1->instanceInitFm2opSIG1(sample_rate);
		sig1->fillFm2opSIG1(65536, ftbl1Fm2opSIG1);
		deleteFm2opSIG0(sig0);
		deleteFm2opSIG1(sig1);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst5 = 1.0f / fConst4;
		fConst6 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.9f);
		fHslider1 = FAUSTFLOAT(0.35f);
		fHslider2 = FAUSTFLOAT(0.25f);
		fHslider3 = FAUSTFLOAT(2.2e+02f);
		fHslider4 = FAUSTFLOAT(1.0f);
		fHslider5 = FAUSTFLOAT(3.0f);
		fHslider6 = FAUSTFLOAT(0.6f);
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
			fRec3[l6] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec5[l9] = 0.0f;
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
	
	virtual Fm2op* clone() {
		return new Fm2op();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fm2op");
		ui_interface->addHorizontalSlider("amp_decay", &fHslider0, FAUSTFLOAT(0.9f), FAUSTFLOAT(0.05f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("amp_sustain", &fHslider1, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider6, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("index", &fHslider5, FAUSTFLOAT(3.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("index_decay", &fHslider2, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.01f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("ratio", &fHslider4, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.25f), FAUSTFLOAT(16.0f), FAUSTFLOAT(0.01f));
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
		float fSlow6 = fConst6 * float(fHslider4) * fSlow5;
		float fSlow7 = float(fHslider5);
		float fSlow8 = fConst6 * fSlow5;
		float fSlow9 = 0.85f * float(fHslider6);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			int iTemp1 = 1 - iVec0[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fSlow6 + fRec3[1]);
			fRec3[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = fSlow7 * ftbl0Fm2opSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst5 * fRec1[0], std::max<float>(fSlow4 * (fConst4 - fRec1[0]) + 1.0f, 0.0f)) * (1.0f - fSlow4 * fTemp0));
			float fTemp4 = ((iTemp1) ? 0.0f : fSlow8 + fRec5[1]);
			fRec5[0] = fTemp4 - std::floor(fTemp4);
			int iTemp5 = std::max<int>(0, std::min<int>(int(65536.0f * fRec5[0]), 65535));
			float fTemp6 = fSlow9 * (ftbl0Fm2opSIG0[iTemp5] * std::cos(fTemp3) + ftbl1Fm2opSIG1[iTemp5] * std::sin(fTemp3)) * std::max<float>(0.0f, std::min<float>(fConst3 * fRec1[0], std::max<float>(fSlow3 * (fConst2 - fRec1[0]) + 1.0f, fSlow2)) * (1.0f - fConst1 * fTemp0));
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec3[1] = fRec3[0];
			fRec5[1] = fRec5[0];
		}
	}

};

#endif
