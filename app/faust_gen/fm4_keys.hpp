/* ------------------------------------------------------------
name: "fm4_keys"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Fm4Keys -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Fm4Keys_H__
#define  __Fm4Keys_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Fm4Keys
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

class Fm4KeysSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsFm4KeysSIG0() {
		return 0;
	}
	int getNumOutputsFm4KeysSIG0() {
		return 1;
	}
	
	void instanceInitFm4KeysSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec2[l5] = 0;
		}
	}
	
	void fillFm4KeysSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec2[0] = (iVec2[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec2[1] = iVec2[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static Fm4KeysSIG0* newFm4KeysSIG0() { return (Fm4KeysSIG0*)new Fm4KeysSIG0(); }
static void deleteFm4KeysSIG0(Fm4KeysSIG0* dsp) { delete dsp; }

static float ftbl0Fm4KeysSIG0[65536];

class Fm4Keys : public dsp {
	
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
	float fConst2;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fConst3;
	float fRec4[2];
	FAUSTFLOAT fHslider4;
	float fRec5[2];
	FAUSTFLOAT fHslider5;
	FAUSTFLOAT fHslider6;
	float fRec3[2];
	FAUSTFLOAT fHslider7;
	float fRec7[2];
	float fRec6[2];
	FAUSTFLOAT fHslider8;
	float fRec10[2];
	float fRec9[2];
	float fRec8[2];
	FAUSTFLOAT fHslider9;
	
 public:
	Fm4Keys() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Fm4Keys -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/are:author", "Julius O. Smith III, revised by Stephane Letz");
		m->declare("envelopes.lib/are:licence", "STK-4.3");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "fm4_keys.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fm4_keys");
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
		Fm4KeysSIG0* sig0 = newFm4KeysSIG0();
		sig0->instanceInitFm4KeysSIG0(sample_rate);
		sig0->fillFm4KeysSIG0(65536, ftbl0Fm4KeysSIG0);
		deleteFm4KeysSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 0.3f / std::max<float>(1.0f, 0.25f * fConst0);
		fConst2 = 0.45f * fConst0;
		fConst3 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.5f);
		fHslider1 = FAUSTFLOAT(0.003f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fHslider3 = FAUSTFLOAT(7.0f);
		fHslider4 = FAUSTFLOAT(0.35f);
		fHslider5 = FAUSTFLOAT(1.4f);
		fHslider6 = FAUSTFLOAT(3.0f);
		fHslider7 = FAUSTFLOAT(2.0f);
		fHslider8 = FAUSTFLOAT(0.35f);
		fHslider9 = FAUSTFLOAT(0.5f);
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
			fRec5[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec3[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec6[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec10[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec9[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec8[l13] = 0.0f;
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
	
	virtual Fm4Keys* clone() {
		return new Fm4Keys();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fm4_keys");
		ui_interface->addHorizontalSlider("algo", &fHslider8, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.003f), FAUSTFLOAT(0.001f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider9, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("index", &fHslider5, FAUSTFLOAT(1.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("index_decay", &fHslider4, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.02f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("ratio2", &fHslider7, FAUSTFLOAT(2.0f), FAUSTFLOAT(0.25f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("ratio3", &fHslider6, FAUSTFLOAT(3.0f), FAUSTFLOAT(0.25f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("ratio4", &fHslider3, FAUSTFLOAT(7.0f), FAUSTFLOAT(0.25f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("release", &fHslider0, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.02f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.001f));
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
		float fSlow6 = float(fHslider3) * fSlow5;
		float fSlow7 = fConst3 * fSlow6 * float(fSlow6 < fConst2);
		int iSlow8 = fSlow0 > 0.0f;
		float fSlow9 = 0.1447178f * ((iSlow8) ? 0.001f : float(fHslider4));
		int iSlow10 = std::fabs(fSlow9) < 1.1920929e-07f;
		float fSlow11 = ((iSlow10) ? 0.0f : std::exp(-(fConst3 / ((iSlow10) ? 1.0f : fSlow9))));
		float fSlow12 = (1.0f - fSlow11) * ((iSlow8) ? float(iSlow8) : 0.0f);
		float fSlow13 = float(fHslider5);
		float fSlow14 = fSlow5 * float(fHslider6);
		float fSlow15 = float(fSlow14 < fConst2);
		float fSlow16 = fConst3 * fSlow14;
		float fSlow17 = fSlow5 * float(fHslider7);
		float fSlow18 = float(fSlow17 < fConst2);
		float fSlow19 = fConst3 * fSlow17 * fSlow18;
		float fSlow20 = 0.8f * fSlow13;
		float fSlow21 = float(fSlow5 < fConst2);
		float fSlow22 = fConst3 * fSlow5;
		float fSlow23 = float(fHslider8);
		float fSlow24 = 0.5f * fSlow13;
		float fSlow25 = fConst3 * fSlow17;
		float fSlow26 = 1.0f - fSlow23;
		float fSlow27 = 0.8f * float(fHslider9);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fSlow7 + fRec4[1]);
			fRec4[0] = fTemp1 - std::floor(fTemp1);
			fRec5[0] = fSlow12 + fSlow11 * fRec5[1];
			float fTemp2 = fRec5[0] * ftbl0Fm4KeysSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))];
			float fTemp3 = ((iTemp0) ? 0.0f : fRec3[1] + fSlow16 * (fSlow15 + fSlow13 * fTemp2));
			fRec3[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = ((iTemp0) ? 0.0f : fSlow19 + fRec7[1]);
			fRec7[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = ((iTemp0) ? 0.0f : fRec6[1] + fSlow22 * (fSlow21 + fSlow20 * fRec5[0] * ftbl0Fm4KeysSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))]));
			fRec6[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp0) ? 0.0f : fRec10[1] + fSlow16 * (fSlow15 + fSlow24 * fTemp2));
			fRec10[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = ((iTemp0) ? 0.0f : fRec9[1] + fSlow25 * (fSlow18 + fSlow13 * fRec5[0] * ftbl0Fm4KeysSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))]));
			fRec9[0] = fTemp7 - std::floor(fTemp7);
			float fTemp8 = ((iTemp0) ? 0.0f : fRec8[1] + fSlow22 * (fSlow21 + fSlow13 * fRec5[0] * ftbl0Fm4KeysSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))]));
			fRec8[0] = fTemp8 - std::floor(fTemp8);
			float fTemp9 = fSlow27 * (fSlow26 * ftbl0Fm4KeysSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + fSlow23 * (0.62f * ftbl0Fm4KeysSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] + 0.38f * ftbl0Fm4KeysSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))])) * std::max<float>(0.0f, std::min<float>(fSlow4 * fRec1[0], std::max<float>(fConst1 * (fSlow3 - fRec1[0]) + 1.0f, 0.7f)) * (1.0f - fSlow2 * float(iRec0[0])));
			output0[i0] = FAUSTFLOAT(fTemp9);
			output1[i0] = FAUSTFLOAT(fTemp9);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec4[1] = fRec4[0];
			fRec5[1] = fRec5[0];
			fRec3[1] = fRec3[0];
			fRec7[1] = fRec7[0];
			fRec6[1] = fRec6[0];
			fRec10[1] = fRec10[0];
			fRec9[1] = fRec9[0];
			fRec8[1] = fRec8[0];
		}
	}

};

#endif
