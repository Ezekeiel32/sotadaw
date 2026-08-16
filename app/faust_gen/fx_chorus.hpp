/* ------------------------------------------------------------
name: "fx_chorus"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxChorus -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxChorus_H__
#define  __FxChorus_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxChorus
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

class FxChorusSIG0 {
	
  private:
	
	int iVec1[2];
	int iRec0[2];
	
  public:
	
	int getNumInputsFxChorusSIG0() {
		return 0;
	}
	int getNumOutputsFxChorusSIG0() {
		return 1;
	}
	
	void instanceInitFxChorusSIG0(int sample_rate) {
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
	}
	
	void fillFxChorusSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec1[0] = 1;
			iRec0[0] = (iVec1[1] + iRec0[1]) % 65536;
			table[i1] = std::cos(9.58738e-05f * float(iRec0[0]));
			iVec1[1] = iVec1[0];
			iRec0[1] = iRec0[0];
		}
	}

};

static FxChorusSIG0* newFxChorusSIG0() { return (FxChorusSIG0*)new FxChorusSIG0(); }
static void deleteFxChorusSIG0(FxChorusSIG0* dsp) { delete dsp; }

class FxChorusSIG1 {
	
  private:
	
	int iVec3[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsFxChorusSIG1() {
		return 0;
	}
	int getNumOutputsFxChorusSIG1() {
		return 1;
	}
	
	void instanceInitFxChorusSIG1(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec3[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec2[l6] = 0;
		}
	}
	
	void fillFxChorusSIG1(int count, float* table) {
		for (int i2 = 0; i2 < count; i2 = i2 + 1) {
			iVec3[0] = 1;
			iRec2[0] = (iVec3[1] + iRec2[1]) % 65536;
			table[i2] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec3[1] = iVec3[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static FxChorusSIG1* newFxChorusSIG1() { return (FxChorusSIG1*)new FxChorusSIG1(); }
static void deleteFxChorusSIG1(FxChorusSIG1* dsp) { delete dsp; }

static float ftbl0FxChorusSIG0[65536];
static float ftbl1FxChorusSIG1[65536];

class FxChorus : public dsp {
	
 private:
	
	int IOTA0;
	float fVec0[8192];
	int iVec2[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fVec4[8192];
	
 public:
	FxChorus() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxChorus -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/fdelay4:author", "Julius O. Smith III");
		m->declare("delays.lib/fdelayltv:author", "Julius O. Smith III");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("filename", "fx_chorus.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_chorus");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
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
		FxChorusSIG0* sig0 = newFxChorusSIG0();
		sig0->instanceInitFxChorusSIG0(sample_rate);
		sig0->fillFxChorusSIG0(65536, ftbl0FxChorusSIG0);
		FxChorusSIG1* sig1 = newFxChorusSIG1();
		sig1->instanceInitFxChorusSIG1(sample_rate);
		sig1->fillFxChorusSIG1(65536, ftbl1FxChorusSIG1);
		deleteFxChorusSIG0(sig0);
		deleteFxChorusSIG1(sig1);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.8f);
		fHslider1 = FAUSTFLOAT(0.5f);
		fHslider2 = FAUSTFLOAT(3.0f);
		fHslider3 = FAUSTFLOAT(0.4f);
	}
	
	virtual void instanceClear() {
		IOTA0 = 0;
		for (int l0 = 0; l0 < 8192; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iVec2[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec1[l4] = 0.0f;
		}
		for (int l7 = 0; l7 < 8192; l7 = l7 + 1) {
			fVec4[l7] = 0.0f;
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
	
	virtual FxChorus* clone() {
		return new FxChorus();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_chorus");
		ui_interface->addHorizontalSlider("depth", &fHslider1, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("mix", &fHslider3, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("rate", &fHslider0, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.05f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("voices", &fHslider2, FAUSTFLOAT(3.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(3.0f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst1 * float(fHslider0);
		float fSlow1 = 0.007f * float(fHslider1);
		float fSlow2 = float(fHslider2);
		float fSlow3 = float(fSlow2 >= 3.0f);
		float fSlow4 = float(fSlow2 >= 2.0f);
		float fSlow5 = float(fHslider3);
		float fSlow6 = std::sqrt(std::min<float>(1.0f, fSlow5)) / std::max<float>(1.0f, fSlow2);
		float fSlow7 = std::sqrt(std::max<float>(0.0f, 1.0f - fSlow5));
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			fVec0[IOTA0 & 8191] = fTemp0;
			iVec2[0] = 1;
			float fTemp1 = ((1 - iVec2[1]) ? 0.0f : fSlow0 + fRec1[1]);
			fRec1[0] = fTemp1 - std::floor(fTemp1);
			int iTemp2 = std::max<int>(0, std::min<int>(int(65536.0f * fRec1[0]), 65535));
			float fTemp3 = ftbl0FxChorusSIG0[iTemp2];
			float fTemp4 = ftbl1FxChorusSIG1[iTemp2];
			float fTemp5 = fConst0 * (0.018f - fSlow1 * (0.4902608f * fTemp4 + 0.8715758f * fTemp3));
			float fTemp6 = fTemp5 + -1.499995f;
			int iTemp7 = int(fTemp6);
			float fTemp8 = std::floor(fTemp6);
			float fTemp9 = fTemp5 + (-3.0f - fTemp8);
			float fTemp10 = fTemp5 + (-2.0f - fTemp8);
			float fTemp11 = fTemp5 + (-1.0f - fTemp8);
			float fTemp12 = fTemp5 - fTemp8;
			float fTemp13 = fTemp12 * fTemp11;
			float fTemp14 = fTemp13 * fTemp10;
			float fTemp15 = fConst0 * (fSlow1 * (0.86320937f * fTemp3 - 0.5048461f * fTemp4) + 0.018f);
			float fTemp16 = fTemp15 + -1.499995f;
			int iTemp17 = int(fTemp16);
			float fTemp18 = std::floor(fTemp16);
			float fTemp19 = fTemp15 + (-3.0f - fTemp18);
			float fTemp20 = fTemp15 + (-2.0f - fTemp18);
			float fTemp21 = fTemp15 + (-1.0f - fTemp18);
			float fTemp22 = fTemp15 - fTemp18;
			float fTemp23 = fTemp22 * fTemp21;
			float fTemp24 = fTemp23 * fTemp20;
			float fTemp25 = fConst0 * (fSlow1 * fTemp4 + 0.018f);
			float fTemp26 = fTemp25 + -1.499995f;
			int iTemp27 = int(fTemp26);
			float fTemp28 = std::floor(fTemp26);
			float fTemp29 = fTemp25 + (-3.0f - fTemp28);
			float fTemp30 = fTemp25 + (-2.0f - fTemp28);
			float fTemp31 = fTemp25 + (-1.0f - fTemp28);
			float fTemp32 = fTemp25 - fTemp28;
			float fTemp33 = fTemp32 * fTemp31;
			float fTemp34 = fTemp33 * fTemp30;
			output0[i0] = FAUSTFLOAT(fSlow7 * fTemp0 + fSlow6 * ((fTemp25 + (-4.0f - fTemp28)) * (fTemp29 * (fTemp30 * (0.041666668f * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp27))) & 8191] * fTemp31 - 0.16666667f * fTemp32 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp27 + 1))) & 8191]) + 0.25f * fTemp33 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp27 + 2))) & 8191]) - 0.16666667f * fTemp34 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp27 + 3))) & 8191]) + 0.041666668f * fTemp34 * fTemp29 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp27 + 4))) & 8191] + fSlow4 * ((fTemp15 + (-4.0f - fTemp18)) * (fTemp19 * (fTemp20 * (0.041666668f * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp17))) & 8191] * fTemp21 - 0.16666667f * fTemp22 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp17 + 1))) & 8191]) + 0.25f * fTemp23 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp17 + 2))) & 8191]) - 0.16666667f * fTemp24 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp17 + 3))) & 8191]) + 0.041666668f * fTemp24 * fTemp19 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp17 + 4))) & 8191]) + fSlow3 * ((fTemp5 + (-4.0f - fTemp8)) * (fTemp9 * (fTemp10 * (0.041666668f * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp7))) & 8191] * fTemp11 - 0.16666667f * fTemp12 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp7 + 1))) & 8191]) + 0.25f * fTemp13 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp7 + 2))) & 8191]) - 0.16666667f * fTemp14 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp7 + 3))) & 8191]) + 0.041666668f * fTemp14 * fTemp9 * fVec0[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp7 + 4))) & 8191])));
			float fTemp35 = float(input1[i0]);
			fVec4[IOTA0 & 8191] = fTemp35;
			float fTemp36 = fConst0 * (fSlow1 * (0.49164832f * fTemp4 + 0.8707939f * fTemp3) + 0.018f);
			float fTemp37 = fTemp36 + -1.499995f;
			int iTemp38 = int(fTemp37);
			float fTemp39 = std::floor(fTemp37);
			float fTemp40 = fTemp36 + (-3.0f - fTemp39);
			float fTemp41 = fTemp36 + (-2.0f - fTemp39);
			float fTemp42 = fTemp36 + (-1.0f - fTemp39);
			float fTemp43 = fTemp36 - fTemp39;
			float fTemp44 = fTemp43 * fTemp42;
			float fTemp45 = fTemp44 * fTemp41;
			float fTemp46 = fConst0 * (fSlow1 * (0.50347066f * fTemp4 - 0.8640123f * fTemp3) + 0.018f);
			float fTemp47 = fTemp46 + -1.499995f;
			int iTemp48 = int(fTemp47);
			float fTemp49 = std::floor(fTemp47);
			float fTemp50 = fTemp46 + (-3.0f - fTemp49);
			float fTemp51 = fTemp46 + (-2.0f - fTemp49);
			float fTemp52 = fTemp46 + (-1.0f - fTemp49);
			float fTemp53 = fTemp46 - fTemp49;
			float fTemp54 = fTemp53 * fTemp52;
			float fTemp55 = fTemp54 * fTemp51;
			float fTemp56 = fConst0 * (fSlow1 * (0.0015926529f * fTemp3 - 0.99999875f * fTemp4) + 0.018f);
			float fTemp57 = fTemp56 + -1.499995f;
			int iTemp58 = int(fTemp57);
			float fTemp59 = std::floor(fTemp57);
			float fTemp60 = fTemp56 + (-3.0f - fTemp59);
			float fTemp61 = fTemp56 + (-2.0f - fTemp59);
			float fTemp62 = fTemp56 + (-1.0f - fTemp59);
			float fTemp63 = fTemp56 - fTemp59;
			float fTemp64 = fTemp63 * fTemp62;
			float fTemp65 = fTemp64 * fTemp61;
			output1[i0] = FAUSTFLOAT(fSlow7 * fTemp35 + fSlow6 * ((fTemp56 + (-4.0f - fTemp59)) * (fTemp60 * (fTemp61 * (0.041666668f * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp58))) & 8191] * fTemp62 - 0.16666667f * fTemp63 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp58 + 1))) & 8191]) + 0.25f * fTemp64 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp58 + 2))) & 8191]) - 0.16666667f * fTemp65 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp58 + 3))) & 8191]) + 0.041666668f * fTemp65 * fTemp60 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp58 + 4))) & 8191] + fSlow4 * ((fTemp46 + (-4.0f - fTemp49)) * (fTemp50 * (fTemp51 * (0.041666668f * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp48))) & 8191] * fTemp52 - 0.16666667f * fTemp53 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp48 + 1))) & 8191]) + 0.25f * fTemp54 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp48 + 2))) & 8191]) - 0.16666667f * fTemp55 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp48 + 3))) & 8191]) + 0.041666668f * fTemp55 * fTemp50 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp48 + 4))) & 8191]) + fSlow3 * ((fTemp36 + (-4.0f - fTemp39)) * (fTemp40 * (fTemp41 * (0.041666668f * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp38))) & 8191] * fTemp42 - 0.16666667f * fTemp43 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp38 + 1))) & 8191]) + 0.25f * fTemp44 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp38 + 2))) & 8191]) - 0.16666667f * fTemp45 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp38 + 3))) & 8191]) + 0.041666668f * fTemp45 * fTemp40 * fVec4[(IOTA0 - std::min<int>(4096, std::max<int>(0, iTemp38 + 4))) & 8191])));
			IOTA0 = IOTA0 + 1;
			iVec2[1] = iVec2[0];
			fRec1[1] = fRec1[0];
		}
	}

};

#endif
