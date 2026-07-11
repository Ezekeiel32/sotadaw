/* ------------------------------------------------------------
name: "kick_psy"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn KickPsy -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __KickPsy_H__
#define  __KickPsy_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS KickPsy
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

class KickPsySIG0 {
	
  private:
	
	int iVec2[2];
	int iRec3[2];
	
  public:
	
	int getNumInputsKickPsySIG0() {
		return 0;
	}
	int getNumOutputsKickPsySIG0() {
		return 1;
	}
	
	void instanceInitKickPsySIG0(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec2[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec3[l6] = 0;
		}
	}
	
	void fillKickPsySIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec3[0] = (iVec2[1] + iRec3[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec3[0]));
			iVec2[1] = iVec2[0];
			iRec3[1] = iRec3[0];
		}
	}

};

static KickPsySIG0* newKickPsySIG0() { return (KickPsySIG0*)new KickPsySIG0(); }
static void deleteKickPsySIG0(KickPsySIG0* dsp) { delete dsp; }

static float KickPsy_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0KickPsySIG0[65536];

class KickPsy : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	int iRec1[2];
	float fRec0[3];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst8;
	float fConst9;
	float fConst10;
	float fConst11;
	float fConst12;
	float fConst13;
	FAUSTFLOAT fHslider0;
	float fConst14;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst15;
	float fRec4[2];
	FAUSTFLOAT fHslider3;
	
 public:
	KickPsy() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn KickPsy -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "kick_psy.dsp");
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
		m->declare("name", "kick_psy");
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
		KickPsySIG0* sig0 = newKickPsySIG0();
		sig0->instanceInitKickPsySIG0(sample_rate);
		sig0->fillKickPsySIG0(65536, ftbl0KickPsySIG0);
		deleteKickPsySIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(8796.459f / fConst0);
		float fConst2 = KickPsy_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = std::max<float>(1.0f, 0.0004f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.007f * fConst0);
		fConst11 = 0.55f / (fConst2 * fConst6);
		fConst12 = std::max<float>(1.0f, 0.0008f * fConst0);
		fConst13 = 1.0f / fConst12;
		fConst14 = 1.0f / std::max<float>(1.0f, 0.045f * fConst0);
		fConst15 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.26f);
		fHslider1 = FAUSTFLOAT(12.0f);
		fHslider2 = FAUSTFLOAT(5e+01f);
		fHslider3 = FAUSTFLOAT(0.9f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec0[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fVec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec2[l4] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
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
	
	virtual KickPsy* clone() {
		return new KickPsy();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("kick_psy");
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.26f), FAUSTFLOAT(0.08f), FAUSTFLOAT(0.8f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(5e+01f), FAUSTFLOAT(25.0f), FAUSTFLOAT(1.2e+02f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.9f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("punch", &fHslider1, FAUSTFLOAT(12.0f), FAUSTFLOAT(2.0f), FAUSTFLOAT(24.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow2 = float(fHslider1);
		float fSlow3 = fConst15 * float(fHslider2);
		float fSlow4 = float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			iRec1[0] = 1103515245 * iRec1[1] + 12345;
			fRec0[0] = 4.656613e-10f * float(iRec1[0]) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			fVec1[0] = fSlow0;
			iRec2[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec2[1] + (iRec2[1] > 0));
			float fTemp0 = float(iRec2[0]);
			float fTemp1 = fConst13 * fTemp0;
			float fTemp2 = fConst12 - fTemp0;
			float fTemp3 = ((1 - iVec0[1]) ? 0.0f : fRec4[1] + fSlow3 * (fSlow2 * KickPsy_faustpower2_f(std::max<float>(0.0f, std::min<float>(fTemp1, fConst14 * fTemp2 + 1.0f))) + 1.0f));
			fRec4[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = tanhf(fSlow4 * (1.15f * ftbl0KickPsySIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fTemp1, fSlow1 * fTemp2 + 1.0f)) + fConst11 * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f)) * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1])));
			output0[i0] = FAUSTFLOAT(fTemp4);
			output1[i0] = FAUSTFLOAT(fTemp4);
			iVec0[1] = iVec0[0];
			iRec1[1] = iRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec4[1] = fRec4[0];
		}
	}

};

#endif
