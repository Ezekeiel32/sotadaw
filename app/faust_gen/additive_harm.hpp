/* ------------------------------------------------------------
name: "additive_harm"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn AdditiveHarm -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __AdditiveHarm_H__
#define  __AdditiveHarm_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS AdditiveHarm
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

class AdditiveHarmSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsAdditiveHarmSIG0() {
		return 0;
	}
	int getNumOutputsAdditiveHarmSIG0() {
		return 1;
	}
	
	void instanceInitAdditiveHarmSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec2[l5] = 0;
		}
	}
	
	void fillAdditiveHarmSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec2[0] = (iVec2[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec2[1] = iVec2[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static AdditiveHarmSIG0* newAdditiveHarmSIG0() { return (AdditiveHarmSIG0*)new AdditiveHarmSIG0(); }
static void deleteAdditiveHarmSIG0(AdditiveHarmSIG0* dsp) { delete dsp; }

static float ftbl0AdditiveHarmSIG0[65536];

class AdditiveHarm : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fRec1[2];
	FAUSTFLOAT fHslider1;
	float fConst1;
	FAUSTFLOAT fHslider2;
	float fConst2;
	float fRec3[2];
	FAUSTFLOAT fHslider3;
	float fConst3;
	float fRec4[2];
	float fConst4;
	float fRec5[2];
	float fConst5;
	float fRec6[2];
	FAUSTFLOAT fHslider4;
	float fConst6;
	float fRec7[2];
	float fConst7;
	float fRec8[2];
	float fConst8;
	float fRec9[2];
	float fConst9;
	float fRec10[2];
	FAUSTFLOAT fHslider5;
	
 public:
	AdditiveHarm() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn AdditiveHarm -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "additive_harm.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "additive_harm");
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
		AdditiveHarmSIG0* sig0 = newAdditiveHarmSIG0();
		sig0->instanceInitAdditiveHarmSIG0(sample_rate);
		sig0->fillAdditiveHarmSIG0(65536, ftbl0AdditiveHarmSIG0);
		deleteAdditiveHarmSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 0.2f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst2 = 8.0f / fConst0;
		fConst3 = 6.0f / fConst0;
		fConst4 = 4.0f / fConst0;
		fConst5 = 2.0f / fConst0;
		fConst6 = 7.0f / fConst0;
		fConst7 = 5.0f / fConst0;
		fConst8 = 3.0f / fConst0;
		fConst9 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.4f);
		fHslider1 = FAUSTFLOAT(0.01f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fHslider3 = FAUSTFLOAT(0.5f);
		fHslider4 = FAUSTFLOAT(0.5f);
		fHslider5 = FAUSTFLOAT(0.75f);
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
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec5[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec7[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec8[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec9[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec10[l13] = 0.0f;
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
	
	virtual AdditiveHarm* clone() {
		return new AdditiveHarm();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("additive_harm");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.01f), FAUSTFLOAT(0.001f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bright", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(3e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.75f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("odd", &fHslider4, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("release", &fHslider0, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.02f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow4 = 1.0f / fSlow3;
		float fSlow5 = float(fHslider2);
		float fSlow6 = fConst2 * fSlow5;
		float fSlow7 = 2.0f - 1.3f * float(fHslider3);
		float fSlow8 = 1.0f / std::pow(8.0f, fSlow7);
		float fSlow9 = fConst3 * fSlow5;
		float fSlow10 = 1.0f / std::pow(6.0f, fSlow7);
		float fSlow11 = fConst4 * fSlow5;
		float fSlow12 = 1.0f / std::pow(4.0f, fSlow7);
		float fSlow13 = fConst5 * fSlow5;
		float fSlow14 = 1.0f / std::pow(2.0f, fSlow7);
		float fSlow15 = float(fHslider4);
		float fSlow16 = 1.0f - fSlow15;
		float fSlow17 = fConst6 * fSlow5;
		float fSlow18 = 1.0f / std::pow(7.0f, fSlow7);
		float fSlow19 = fConst7 * fSlow5;
		float fSlow20 = 1.0f / std::pow(5.0f, fSlow7);
		float fSlow21 = fConst8 * fSlow5;
		float fSlow22 = 1.0f / std::pow(3.0f, fSlow7);
		float fSlow23 = fConst9 * fSlow5;
		float fSlow24 = 1.0f / std::pow(1.0f, fSlow7);
		float fSlow25 = 0.5f * (fSlow15 + 1.0f);
		float fSlow26 = 0.5f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fSlow6 + fRec3[1]);
			fRec3[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = ((iTemp0) ? 0.0f : fSlow9 + fRec4[1]);
			fRec4[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = ((iTemp0) ? 0.0f : fSlow11 + fRec5[1]);
			fRec5[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = ((iTemp0) ? 0.0f : fSlow13 + fRec6[1]);
			fRec6[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = ((iTemp0) ? 0.0f : fSlow17 + fRec7[1]);
			fRec7[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp0) ? 0.0f : fSlow19 + fRec8[1]);
			fRec8[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = ((iTemp0) ? 0.0f : fSlow21 + fRec9[1]);
			fRec9[0] = fTemp7 - std::floor(fTemp7);
			float fTemp8 = ((iTemp0) ? 0.0f : fSlow23 + fRec10[1]);
			fRec10[0] = fTemp8 - std::floor(fTemp8);
			float fTemp9 = fSlow26 * (fSlow25 * (fSlow24 * ftbl0AdditiveHarmSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))] + fSlow22 * ftbl0AdditiveHarmSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] + fSlow20 * ftbl0AdditiveHarmSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + fSlow18 * ftbl0AdditiveHarmSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))]) + fSlow16 * (fSlow14 * ftbl0AdditiveHarmSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] + fSlow12 * ftbl0AdditiveHarmSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec5[0]), 65535))] + fSlow10 * ftbl0AdditiveHarmSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] + fSlow8 * ftbl0AdditiveHarmSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))])) * std::max<float>(0.0f, std::min<float>(fSlow4 * fRec1[0], std::max<float>(fConst1 * (fSlow3 - fRec1[0]) + 1.0f, 0.8f)) * (1.0f - fSlow2 * float(iRec0[0])));
			output0[i0] = FAUSTFLOAT(fTemp9);
			output1[i0] = FAUSTFLOAT(fTemp9);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec3[1] = fRec3[0];
			fRec4[1] = fRec4[0];
			fRec5[1] = fRec5[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fRec8[1] = fRec8[0];
			fRec9[1] = fRec9[0];
			fRec10[1] = fRec10[0];
		}
	}

};

#endif
