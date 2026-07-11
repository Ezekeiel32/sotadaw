/* ------------------------------------------------------------
name: "kalimba"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Kalimba -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Kalimba_H__
#define  __Kalimba_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Kalimba
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

class KalimbaSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec3[2];
	
  public:
	
	int getNumInputsKalimbaSIG0() {
		return 0;
	}
	int getNumOutputsKalimbaSIG0() {
		return 1;
	}
	
	void instanceInitKalimbaSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec3[l5] = 0;
		}
	}
	
	void fillKalimbaSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec3[0] = (iVec2[1] + iRec3[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec3[0]));
			iVec2[1] = iVec2[0];
			iRec3[1] = iRec3[0];
		}
	}

};

static KalimbaSIG0* newKalimbaSIG0() { return (KalimbaSIG0*)new KalimbaSIG0(); }
static void deleteKalimbaSIG0(KalimbaSIG0* dsp) { delete dsp; }

static float Kalimba_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0KalimbaSIG0[65536];

class Kalimba : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec1[2];
	float fConst7;
	float fRec2[2];
	float fConst8;
	float fConst9;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst10;
	float fRec4[2];
	int iRec6[2];
	float fConst11;
	float fConst12;
	float fConst13;
	int iRec7[2];
	FAUSTFLOAT fHslider2;
	float fVec3[2];
	float fConst14;
	float fConst15;
	float fConst16;
	float fRec5[2];
	float fConst17;
	float fConst18;
	float fConst19;
	float fRec8[2];
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fRec0[3];
	float fConst20;
	
 public:
	Kalimba() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Kalimba -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "kalimba.dsp");
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
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "kalimba");
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
		KalimbaSIG0* sig0 = newKalimbaSIG0();
		sig0->instanceInitKalimbaSIG0(sample_rate);
		sig0->fillKalimbaSIG0(65536, ftbl0KalimbaSIG0);
		deleteKalimbaSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(21991.148f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / Kalimba_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 1.4142135f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		fConst7 = 1.0f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst8 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / fConst0;
		fConst11 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst12 = 1.0f / fConst11;
		fConst13 = 1.0f / std::max<float>(1.0f, 0.006f * fConst0);
		fConst14 = 1.0f / std::tan(3769.9111f / fConst0);
		fConst15 = 1.0f - fConst14;
		fConst16 = 1.0f / (fConst14 + 1.0f);
		fConst17 = 1.0f / std::max<float>(1.0f, 0.04f * fConst0);
		fConst18 = 1.0f / std::max<float>(1.0f, 0.09f * fConst0);
		fConst19 = 2.08f / fConst0;
		fConst20 = 0.664f / fConst5;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.4f);
		fHslider1 = FAUSTFLOAT(4.4e+02f);
		fHslider2 = FAUSTFLOAT(0.3f);
		fHslider3 = FAUSTFLOAT(0.35f);
		fHslider4 = FAUSTFLOAT(0.65f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iRec6[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec7[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fVec3[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec5[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec8[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
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
	
	virtual Kalimba* clone() {
		return new Kalimba();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("kalimba");
		ui_interface->addHorizontalSlider("click", &fHslider2, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.1f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.65f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sparkle", &fHslider3, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = float(fHslider1);
		float fSlow4 = fConst10 * fSlow3;
		float fSlow5 = 4.656613e-10f * float(fHslider2);
		float fSlow6 = fConst19 * fSlow3;
		float fSlow7 = float(fHslider3);
		float fSlow8 = float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec1[0] = iSlow1 * (iRec1[1] + 1);
			float fTemp0 = float(iRec1[0]);
			fRec2[0] = fSlow0 + fRec2[1] * float(fVec1[1] >= fSlow0);
			float fTemp1 = fConst9 * fRec2[0];
			float fTemp2 = fConst8 - fRec2[0];
			int iTemp3 = 1 - iVec0[1];
			float fTemp4 = ((iTemp3) ? 0.0f : fSlow4 + fRec4[1]);
			fRec4[0] = fTemp4 - std::floor(fTemp4);
			iRec6[0] = (iRec6[1] + (iRec6[1] > 0)) * (fSlow0 <= fVec1[1]) + (fSlow0 > fVec1[1]);
			float fTemp5 = float(iRec6[0]);
			iRec7[0] = 1103515245 * iRec7[1] + 12345;
			float fTemp6 = fSlow5 * float(iRec7[0]) * std::max<float>(0.0f, std::min<float>(fConst12 * fTemp5, fConst13 * (fConst11 - fTemp5) + 1.0f));
			fVec3[0] = fTemp6;
			fRec5[0] = -(fConst16 * (fConst15 * fRec5[1] - fConst14 * (fTemp6 - fVec3[1])));
			float fTemp7 = ((iTemp3) ? 0.0f : fSlow6 + fRec8[1]);
			fRec8[0] = fTemp7 - std::floor(fTemp7);
			fRec0[0] = fSlow8 * (fSlow7 * ftbl0KalimbaSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fTemp1, std::max<float>(fConst18 * fTemp2 + 1.0f, 0.0f)) * (1.0f - fConst17 * fTemp0)) + fRec5[0] + ftbl0KalimbaSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fTemp1, std::max<float>(fSlow2 * fTemp2 + 1.0f, 0.0f)) * (1.0f - fConst7 * fTemp0))) - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp8 = fConst20 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp8);
			output1[i0] = FAUSTFLOAT(fTemp8);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			fRec4[1] = fRec4[0];
			iRec6[1] = iRec6[0];
			iRec7[1] = iRec7[0];
			fVec3[1] = fVec3[0];
			fRec5[1] = fRec5[0];
			fRec8[1] = fRec8[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
