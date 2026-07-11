/* ------------------------------------------------------------
name: "fx_widen"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxWiden -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxWiden_H__
#define  __FxWiden_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxWiden
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

class FxWidenSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec0[2];
	
  public:
	
	int getNumInputsFxWidenSIG0() {
		return 0;
	}
	int getNumOutputsFxWidenSIG0() {
		return 1;
	}
	
	void instanceInitFxWidenSIG0(int sample_rate) {
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iVec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec0[l3] = 0;
		}
	}
	
	void fillFxWidenSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec0[0] = (iVec2[1] + iRec0[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec0[0]));
			iVec2[1] = iVec2[0];
			iRec0[1] = iRec0[0];
		}
	}

};

static FxWidenSIG0* newFxWidenSIG0() { return (FxWidenSIG0*)new FxWidenSIG0(); }
static void deleteFxWidenSIG0(FxWidenSIG0* dsp) { delete dsp; }

static float ftbl0FxWidenSIG0[65536];

class FxWiden : public dsp {
	
 private:
	
	int IOTA0;
	float fVec0[2048];
	int iVec1[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	float fRec1[2];
	float fConst2;
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider1;
	float fRec2[2];
	
 public:
	FxWiden() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxWiden -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("filename", "fx_widen.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_widen");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
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
		FxWidenSIG0* sig0 = newFxWidenSIG0();
		sig0->instanceInitFxWidenSIG0(sample_rate);
		sig0->fillFxWidenSIG0(65536, ftbl0FxWidenSIG0);
		deleteFxWidenSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / fConst0;
		fConst2 = 0.008f * fConst0;
		fConst3 = 44.1f / fConst0;
		fConst4 = 1.0f - fConst3;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.4f);
		fHslider1 = FAUSTFLOAT(1.4f);
	}
	
	virtual void instanceClear() {
		IOTA0 = 0;
		for (int l0 = 0; l0 < 2048; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec1[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec2[l5] = 0.0f;
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
	
	virtual FxWiden* clone() {
		return new FxWiden();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_widen");
		ui_interface->addHorizontalSlider("rate", &fHslider0, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.05f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("width", &fHslider1, FAUSTFLOAT(1.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst1 * float(fHslider0);
		float fSlow1 = fConst3 * float(fHslider1);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input1[i0]);
			fVec0[IOTA0 & 2047] = fTemp0;
			iVec1[0] = 1;
			float fTemp1 = ((1 - iVec1[1]) ? 0.0f : fSlow0 + fRec1[1]);
			fRec1[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = fConst2 * (0.15f * ftbl0FxWidenSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec1[0]), 65535))] + 1.0f);
			int iTemp3 = int(fTemp2);
			float fTemp4 = std::floor(fTemp2);
			float fTemp5 = (fTemp2 - fTemp4) * fVec0[(IOTA0 - std::min<int>(4097, std::max<int>(0, iTemp3 + 1))) & 2047];
			float fTemp6 = fVec0[(IOTA0 - std::min<int>(4097, std::max<int>(0, iTemp3))) & 2047] * (fTemp4 + (1.0f - fTemp2));
			float fTemp7 = float(input0[i0]);
			fRec2[0] = fSlow1 + fConst4 * fRec2[1];
			float fTemp8 = fRec2[0] * (fTemp7 - (fTemp6 + fTemp5));
			float fTemp9 = fTemp5 + fTemp7 + fTemp6;
			output0[i0] = FAUSTFLOAT(0.5f * (fTemp9 + fTemp8));
			output1[i0] = FAUSTFLOAT(0.5f * (fTemp9 - fTemp8));
			IOTA0 = IOTA0 + 1;
			iVec1[1] = iVec1[0];
			fRec1[1] = fRec1[0];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
