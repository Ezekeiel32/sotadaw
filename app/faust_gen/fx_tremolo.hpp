/* ------------------------------------------------------------
name: "fx_tremolo"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxTremolo -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxTremolo_H__
#define  __FxTremolo_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxTremolo
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

class FxTremoloSIG0 {
	
  private:
	
	int iVec1[2];
	int iRec1[2];
	
  public:
	
	int getNumInputsFxTremoloSIG0() {
		return 0;
	}
	int getNumOutputsFxTremoloSIG0() {
		return 1;
	}
	
	void instanceInitFxTremoloSIG0(int sample_rate) {
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec1[l2] = 0;
		}
	}
	
	void fillFxTremoloSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec1[0] = 1;
			iRec1[0] = (iVec1[1] + iRec1[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec1[0]));
			iVec1[1] = iVec1[0];
			iRec1[1] = iRec1[0];
		}
	}

};

static FxTremoloSIG0* newFxTremoloSIG0() { return (FxTremoloSIG0*)new FxTremoloSIG0(); }
static void deleteFxTremoloSIG0(FxTremoloSIG0* dsp) { delete dsp; }

class FxTremoloSIG1 {
	
  private:
	
	int iVec2[2];
	int iRec4[2];
	
  public:
	
	int getNumInputsFxTremoloSIG1() {
		return 0;
	}
	int getNumOutputsFxTremoloSIG1() {
		return 1;
	}
	
	void instanceInitFxTremoloSIG1(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec2[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec4[l6] = 0;
		}
	}
	
	void fillFxTremoloSIG1(int count, float* table) {
		for (int i2 = 0; i2 < count; i2 = i2 + 1) {
			iVec2[0] = 1;
			iRec4[0] = (iVec2[1] + iRec4[1]) % 65536;
			table[i2] = std::cos(9.58738e-05f * float(iRec4[0]));
			iVec2[1] = iVec2[0];
			iRec4[1] = iRec4[0];
		}
	}

};

static FxTremoloSIG1* newFxTremoloSIG1() { return (FxTremoloSIG1*)new FxTremoloSIG1(); }
static void deleteFxTremoloSIG1(FxTremoloSIG1* dsp) { delete dsp; }

static float ftbl0FxTremoloSIG0[65536];
static float ftbl1FxTremoloSIG1[65536];

class FxTremolo : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst1;
	FAUSTFLOAT fHslider0;
	float fConst2;
	float fRec2[2];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst3;
	float fRec0[2];
	FAUSTFLOAT fHslider3;
	float fRec3[2];
	
 public:
	FxTremolo() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxTremolo -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_tremolo.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_tremolo");
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
		FxTremoloSIG0* sig0 = newFxTremoloSIG0();
		sig0->instanceInitFxTremoloSIG0(sample_rate);
		sig0->fillFxTremoloSIG0(65536, ftbl0FxTremoloSIG0);
		FxTremoloSIG1* sig1 = newFxTremoloSIG1();
		sig1->instanceInitFxTremoloSIG1(sample_rate);
		sig1->fillFxTremoloSIG1(65536, ftbl1FxTremoloSIG1);
		deleteFxTremoloSIG0(sig0);
		deleteFxTremoloSIG1(sig1);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::exp(-(1e+03f / fConst0));
		fConst2 = 1.0f / fConst0;
		fConst3 = 1.0f - fConst1;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(4.6f);
		fHslider1 = FAUSTFLOAT(0.25f);
		fHslider2 = FAUSTFLOAT(0.5f);
		fHslider3 = FAUSTFLOAT(0.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec0[l4] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec3[l7] = 0.0f;
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
	
	virtual FxTremolo* clone() {
		return new FxTremolo();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_tremolo");
		ui_interface->addHorizontalSlider("depth", &fHslider2, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("rate", &fHslider0, FAUSTFLOAT(4.6f), FAUSTFLOAT(0.1f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("shape", &fHslider1, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("spread", &fHslider3, FAUSTFLOAT(0.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst2 * float(fHslider0);
		float fSlow1 = float(fHslider1);
		float fSlow2 = 0.5f * (1.0f - fSlow1);
		float fSlow3 = float(fHslider2);
		float fSlow4 = 3.14f * float(fHslider3);
		float fSlow5 = std::sin(fSlow4);
		float fSlow6 = std::cos(fSlow4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			float fTemp0 = ((1 - iVec0[1]) ? 0.0f : fSlow0 + fRec2[1]);
			fRec2[0] = fTemp0 - std::floor(fTemp0);
			int iTemp1 = std::max<int>(0, std::min<int>(int(65536.0f * fRec2[0]), 65535));
			float fTemp2 = ftbl0FxTremoloSIG0[iTemp1];
			float fTemp3 = fTemp2 + 1.0f;
			fRec0[0] = fConst3 * (1.0f - fSlow3 * (1.0f - (fSlow2 * fTemp3 + fSlow1 * float((0.5f * fTemp3) > 0.5f)))) + fConst1 * fRec0[1];
			output0[i0] = FAUSTFLOAT(float(input0[i0]) * fRec0[0]);
			float fTemp4 = fSlow6 * fTemp2 + fSlow5 * ftbl1FxTremoloSIG1[iTemp1] + 1.0f;
			fRec3[0] = fConst3 * (1.0f - fSlow3 * (1.0f - (fSlow2 * fTemp4 + fSlow1 * float((0.5f * fTemp4) > 0.5f)))) + fConst1 * fRec3[1];
			output1[i0] = FAUSTFLOAT(float(input1[i0]) * fRec3[0]);
			iVec0[1] = iVec0[0];
			fRec2[1] = fRec2[0];
			fRec0[1] = fRec0[0];
			fRec3[1] = fRec3[0];
		}
	}

};

#endif
