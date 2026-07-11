/* ------------------------------------------------------------
name: "kick_punch_tight"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn KickPunchTight -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __KickPunchTight_H__
#define  __KickPunchTight_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS KickPunchTight
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

class KickPunchTightSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsKickPunchTightSIG0() {
		return 0;
	}
	int getNumOutputsKickPunchTightSIG0() {
		return 1;
	}
	
	void instanceInitKickPunchTightSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec2[l5] = 0;
		}
	}
	
	void fillKickPunchTightSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec2[0] = (iVec2[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec2[1] = iVec2[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static KickPunchTightSIG0* newKickPunchTightSIG0() { return (KickPunchTightSIG0*)new KickPunchTightSIG0(); }
static void deleteKickPunchTightSIG0(KickPunchTightSIG0* dsp) { delete dsp; }

static float ftbl0KickPunchTightSIG0[65536];
static float KickPunchTight_faustpower2_f(float value) {
	return value * value;
}

class KickPunchTight : public dsp {
	
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
	float fConst4;
	FAUSTFLOAT fHslider0;
	float fConst5;
	float fRec3[2];
	FAUSTFLOAT fHslider1;
	float fConst6;
	float fConst7;
	float fConst8;
	FAUSTFLOAT fHslider2;
	int iRec5[2];
	float fConst9;
	FAUSTFLOAT fHslider3;
	float fRec4[2];
	float fConst12;
	float fConst14;
	float fConst16;
	int iRec7[2];
	float fRec6[3];
	float fConst17;
	float fConst18;
	float fConst19;
	FAUSTFLOAT fHslider4;
	float fConst20;
	FAUSTFLOAT fHslider5;
	FAUSTFLOAT fHslider6;
	
 public:
	KickPunchTight() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn KickPunchTight -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "kick_punch_tight.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "kick_punch_tight");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
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
		KickPunchTightSIG0* sig0 = newKickPunchTightSIG0();
		sig0->instanceInitKickPunchTightSIG0(sample_rate);
		sig0->fillKickPunchTightSIG0(65536, ftbl0KickPunchTightSIG0);
		deleteKickPunchTightSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.005f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 1.0f / std::max<float>(1.0f, 0.55f * fConst0);
		fConst5 = 1.0f / fConst0;
		fConst6 = 1.0f / std::max<float>(1.0f, 0.06f * fConst0);
		fConst7 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst8 = 1.0f / fConst7;
		fConst9 = 1.0f / std::max<float>(1.0f, 0.016f * fConst0);
		float fConst10 = std::tan(7853.9814f / fConst0);
		float fConst11 = KickPunchTight_faustpower2_f(fConst10);
		fConst12 = 2.0f * (1.0f - 1.0f / fConst11);
		float fConst13 = 1.0f / fConst10;
		fConst14 = (fConst13 + -1.4142135f) / fConst10 + 1.0f;
		float fConst15 = (fConst13 + 1.4142135f) / fConst10 + 1.0f;
		fConst16 = 1.0f / fConst15;
		fConst17 = std::max<float>(1.0f, 0.0004f * fConst0);
		fConst18 = 1.0f / fConst17;
		fConst19 = 1.0f / std::max<float>(1.0f, 0.008f * fConst0);
		fConst20 = 1.0f / (fConst11 * fConst15);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(52.0f);
		fHslider1 = FAUSTFLOAT(0.7f);
		fHslider2 = FAUSTFLOAT(0.3f);
		fHslider3 = FAUSTFLOAT(2.8f);
		fHslider4 = FAUSTFLOAT(0.6f);
		fHslider5 = FAUSTFLOAT(1.0f);
		fHslider6 = FAUSTFLOAT(0.9f);
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
			iRec5[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec4[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			iRec7[l9] = 0;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec6[l10] = 0.0f;
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
	
	virtual KickPunchTight* clone() {
		return new KickPunchTight();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("kick_punch_tight");
		ui_interface->addHorizontalSlider("decay", &fHslider2, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.05f), FAUSTFLOAT(1.2f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("drive", &fHslider5, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.2f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("drop", &fHslider3, FAUSTFLOAT(2.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(52.0f), FAUSTFLOAT(25.0f), FAUSTFLOAT(2e+02f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider6, FAUSTFLOAT(0.9f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("punch", &fHslider4, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tail", &fHslider1, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = fConst5 * float(fHslider0);
		float fSlow3 = float(fHslider1);
		float fSlow4 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow5 = float(fHslider3);
		float fSlow6 = fConst20 * float(fHslider4);
		float fSlow7 = float(fHslider5);
		float fSlow8 = float(fHslider6);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			int iTemp1 = 1 - iVec0[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fSlow2 + fRec3[1]);
			fRec3[0] = fTemp2 - std::floor(fTemp2);
			iRec5[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec5[1] + (iRec5[1] > 0));
			float fTemp3 = float(iRec5[0]);
			float fTemp4 = ((iTemp1) ? 0.0f : fRec4[1] + fSlow2 * (fSlow5 * std::max<float>(0.0f, std::min<float>(fConst8 * fTemp3, fConst9 * (fConst7 - fTemp3) + 1.0f)) + 1.0f));
			fRec4[0] = fTemp4 - std::floor(fTemp4);
			iRec7[0] = 1103515245 * iRec7[1] + 12345;
			fRec6[0] = 4.656613e-10f * float(iRec7[0]) - fConst16 * (fConst14 * fRec6[2] + fConst12 * fRec6[1]);
			float fTemp5 = fSlow8 * tanhf(fSlow7 * (fSlow6 * std::max<float>(0.0f, std::min<float>(fConst18 * fTemp3, fConst19 * (fConst17 - fTemp3) + 1.0f)) * (fRec6[0] + fRec6[2] - 2.0f * fRec6[1]) + 1.6f * ftbl0KickPunchTightSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst8 * fRec1[0], std::max<float>(fSlow4 * (fConst7 - fRec1[0]) + 1.0f, 0.0f)) * (1.0f - fConst6 * fTemp0)) + fSlow3 * ftbl0KickPunchTightSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst3 * fRec1[0], std::max<float>(fConst4 * (fConst2 - fRec1[0]) + 1.0f, 0.0f)) * (1.0f - fConst1 * fTemp0))));
			output0[i0] = FAUSTFLOAT(fTemp5);
			output1[i0] = FAUSTFLOAT(fTemp5);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec3[1] = fRec3[0];
			iRec5[1] = iRec5[0];
			fRec4[1] = fRec4[0];
			iRec7[1] = iRec7[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
		}
	}

};

#endif
