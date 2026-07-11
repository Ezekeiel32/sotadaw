/* ------------------------------------------------------------
name: "fx_flanger"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxFlanger -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxFlanger_H__
#define  __FxFlanger_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxFlanger
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

class FxFlangerSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec1[2];
	
  public:
	
	int getNumInputsFxFlangerSIG0() {
		return 0;
	}
	int getNumOutputsFxFlangerSIG0() {
		return 1;
	}
	
	void instanceInitFxFlangerSIG0(int sample_rate) {
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iVec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec1[l3] = 0;
		}
	}
	
	void fillFxFlangerSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec1[0] = (iVec2[1] + iRec1[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec1[0]));
			iVec2[1] = iVec2[0];
			iRec1[1] = iRec1[0];
		}
	}

};

static FxFlangerSIG0* newFxFlangerSIG0() { return (FxFlangerSIG0*)new FxFlangerSIG0(); }
static void deleteFxFlangerSIG0(FxFlangerSIG0* dsp) { delete dsp; }

class FxFlangerSIG1 {
	
  private:
	
	int iVec4[2];
	int iRec4[2];
	
  public:
	
	int getNumInputsFxFlangerSIG1() {
		return 0;
	}
	int getNumOutputsFxFlangerSIG1() {
		return 1;
	}
	
	void instanceInitFxFlangerSIG1(int sample_rate) {
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iVec4[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec4[l8] = 0;
		}
	}
	
	void fillFxFlangerSIG1(int count, float* table) {
		for (int i2 = 0; i2 < count; i2 = i2 + 1) {
			iVec4[0] = 1;
			iRec4[0] = (iVec4[1] + iRec4[1]) % 65536;
			table[i2] = std::cos(9.58738e-05f * float(iRec4[0]));
			iVec4[1] = iVec4[0];
			iRec4[1] = iRec4[0];
		}
	}

};

static FxFlangerSIG1* newFxFlangerSIG1() { return (FxFlangerSIG1*)new FxFlangerSIG1(); }
static void deleteFxFlangerSIG1(FxFlangerSIG1* dsp) { delete dsp; }

static float ftbl0FxFlangerSIG0[65536];
static float ftbl1FxFlangerSIG1[65536];

class FxFlanger : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int iVec0[2];
	FAUSTFLOAT fHslider1;
	int IOTA0;
	float fVec1[2048];
	FAUSTFLOAT fHslider2;
	int fSampleRate;
	float fConst1;
	float fRec2[2];
	FAUSTFLOAT fHslider3;
	float fConst2;
	float fRec0[2];
	float fVec3[2048];
	float fRec3[2];
	
 public:
	FxFlanger() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxFlanger -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("filename", "fx_flanger.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_flanger");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("phaflangers.lib/name", "Faust Phaser and Flanger Library");
		m->declare("phaflangers.lib/version", "1.1.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		FxFlangerSIG0* sig0 = newFxFlangerSIG0();
		sig0->instanceInitFxFlangerSIG0(sample_rate);
		sig0->fillFxFlangerSIG0(65536, ftbl0FxFlangerSIG0);
		FxFlangerSIG1* sig1 = newFxFlangerSIG1();
		sig1->instanceInitFxFlangerSIG1(sample_rate);
		sig1->fillFxFlangerSIG1(65536, ftbl1FxFlangerSIG1);
		deleteFxFlangerSIG0(sig0);
		deleteFxFlangerSIG1(sig1);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / fConst0;
		fConst2 = 0.001f * fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.5f);
		fHslider1 = FAUSTFLOAT(0.45f);
		fHslider2 = FAUSTFLOAT(0.22f);
		fHslider3 = FAUSTFLOAT(0.75f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		IOTA0 = 0;
		for (int l1 = 0; l1 < 2048; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec0[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2048; l6 = l6 + 1) {
			fVec3[l6] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec3[l9] = 0.0f;
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
	
	virtual FxFlanger* clone() {
		return new FxFlanger();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_flanger");
		ui_interface->addHorizontalSlider("depth", &fHslider3, FAUSTFLOAT(0.75f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("feedback", &fHslider1, FAUSTFLOAT(0.45f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.9f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("mix", &fHslider0, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("rate", &fHslider2, FAUSTFLOAT(0.22f), FAUSTFLOAT(0.02f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = 1.0f - fSlow0;
		float fSlow2 = float(fHslider1);
		float fSlow3 = fConst1 * float(fHslider2);
		float fSlow4 = 4.5f * float(fHslider3);
		float fSlow5 = 0.5f * fSlow0;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			iVec0[0] = 1;
			float fTemp1 = fSlow2 * fRec0[1] - fTemp0;
			fVec1[IOTA0 & 2047] = fTemp1;
			float fTemp2 = ((1 - iVec0[1]) ? 0.0f : fSlow3 + fRec2[1]);
			fRec2[0] = fTemp2 - std::floor(fTemp2);
			int iTemp3 = std::max<int>(0, std::min<int>(int(65536.0f * fRec2[0]), 65535));
			float fTemp4 = fConst2 * (fSlow4 * (ftbl0FxFlangerSIG0[iTemp3] + 1.0f) + 1.0f);
			int iTemp5 = int(fTemp4);
			float fTemp6 = std::floor(fTemp4);
			fRec0[0] = fVec1[(IOTA0 - std::min<int>(2049, std::max<int>(0, iTemp5))) & 2047] * (fTemp6 + (1.0f - fTemp4)) + (fTemp4 - fTemp6) * fVec1[(IOTA0 - std::min<int>(2049, std::max<int>(0, iTemp5 + 1))) & 2047];
			output0[i0] = FAUSTFLOAT(fSlow5 * (fTemp0 + fRec0[0]) + fSlow1 * fTemp0);
			float fTemp7 = float(input1[i0]);
			float fTemp8 = fSlow2 * fRec3[1] - fTemp7;
			fVec3[IOTA0 & 2047] = fTemp8;
			float fTemp9 = fConst2 * (fSlow4 * (ftbl1FxFlangerSIG1[iTemp3] + 1.0f) + 1.0f);
			int iTemp10 = int(fTemp9);
			float fTemp11 = std::floor(fTemp9);
			fRec3[0] = fVec3[(IOTA0 - std::min<int>(2049, std::max<int>(0, iTemp10))) & 2047] * (fTemp11 + (1.0f - fTemp9)) + (fTemp9 - fTemp11) * fVec3[(IOTA0 - std::min<int>(2049, std::max<int>(0, iTemp10 + 1))) & 2047];
			output1[i0] = FAUSTFLOAT(fSlow5 * (fTemp7 + fRec3[0]) + fSlow1 * fTemp7);
			iVec0[1] = iVec0[0];
			IOTA0 = IOTA0 + 1;
			fRec2[1] = fRec2[0];
			fRec0[1] = fRec0[0];
			fRec3[1] = fRec3[0];
		}
	}

};

#endif
