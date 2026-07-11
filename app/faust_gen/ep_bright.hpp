/* ------------------------------------------------------------
name: "ep_bright"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn EpBright -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __EpBright_H__
#define  __EpBright_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS EpBright
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

class EpBrightSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsEpBrightSIG0() {
		return 0;
	}
	int getNumOutputsEpBrightSIG0() {
		return 1;
	}
	
	void instanceInitEpBrightSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec2[l5] = 0;
		}
	}
	
	void fillEpBrightSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec2[0] = (iVec2[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec2[1] = iVec2[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static EpBrightSIG0* newEpBrightSIG0() { return (EpBrightSIG0*)new EpBrightSIG0(); }
static void deleteEpBrightSIG0(EpBrightSIG0* dsp) { delete dsp; }

static float ftbl0EpBrightSIG0[65536];

class EpBright : public dsp {
	
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
	float fConst4;
	float fRec3[2];
	float fConst5;
	float fRec4[2];
	FAUSTFLOAT fHslider2;
	int iRec6[2];
	float fConst6;
	float fConst7;
	float fConst8;
	FAUSTFLOAT fHslider3;
	float fConst9;
	float fRec7[2];
	FAUSTFLOAT fHslider4;
	float fRec5[2];
	FAUSTFLOAT fHslider5;
	
 public:
	EpBright() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn EpBright -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "ep_bright.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "ep_bright");
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
		EpBrightSIG0* sig0 = newEpBrightSIG0();
		sig0->instanceInitEpBrightSIG0(sample_rate);
		sig0->fillEpBrightSIG0(65536, ftbl0EpBrightSIG0);
		deleteEpBrightSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.25f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 3.003f / fConst0;
		fConst5 = 2.001f / fConst0;
		fConst6 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst7 = 1.0f / fConst6;
		fConst8 = 1.0f / std::max<float>(1.0f, 0.09f * fConst0);
		fConst9 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(1.4f);
		fHslider1 = FAUSTFLOAT(2.2e+02f);
		fHslider2 = FAUSTFLOAT(0.55f);
		fHslider3 = FAUSTFLOAT(7.0f);
		fHslider4 = FAUSTFLOAT(0.7f);
		fHslider5 = FAUSTFLOAT(0.5f);
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
			iRec6[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec5[l10] = 0.0f;
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
	
	virtual EpBright* clone() {
		return new EpBright();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("ep_bright");
		ui_interface->addHorizontalSlider("bell", &fHslider3, FAUSTFLOAT(7.0f), FAUSTFLOAT(2.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("body", &fHslider2, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(1.4f), FAUSTFLOAT(0.2f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("tine", &fHslider4, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 0.75f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = float(fHslider1);
		float fSlow4 = fConst4 * fSlow3;
		float fSlow5 = fConst5 * fSlow3;
		float fSlow6 = float(fHslider2);
		float fSlow7 = fConst9 * fSlow3 * float(fHslider3);
		float fSlow8 = 0.9f * float(fHslider4);
		float fSlow9 = fConst9 * fSlow3;
		float fSlow10 = 0.34f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fSlow4 + fRec3[1]);
			fRec3[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = ((iTemp0) ? 0.0f : fSlow5 + fRec4[1]);
			fRec4[0] = fTemp2 - std::floor(fTemp2);
			iRec6[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec6[1] + (iRec6[1] > 0));
			float fTemp3 = float(iRec6[0]);
			float fTemp4 = ((iTemp0) ? 0.0f : fSlow7 + fRec7[1]);
			fRec7[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = ((iTemp0) ? 0.0f : fRec5[1] + fSlow9 * (fSlow8 * ftbl0EpBrightSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst7 * fTemp3, fConst8 * (fConst6 - fTemp3) + 1.0f)) + 1.0f));
			fRec5[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = fSlow10 * (ftbl0EpBrightSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec5[0]), 65535))] + fSlow6 * (ftbl0EpBrightSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] + 0.35f * ftbl0EpBrightSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))])) * std::max<float>(0.0f, std::min<float>(fConst3 * fRec1[0], std::max<float>(fSlow2 * (fConst2 - fRec1[0]) + 1.0f, 0.25f)) * (1.0f - fConst1 * float(iRec0[0])));
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec3[1] = fRec3[0];
			fRec4[1] = fRec4[0];
			iRec6[1] = iRec6[0];
			fRec7[1] = fRec7[0];
			fRec5[1] = fRec5[0];
		}
	}

};

#endif
