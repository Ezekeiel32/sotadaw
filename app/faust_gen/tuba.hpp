/* ------------------------------------------------------------
name: "tuba"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Tuba -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Tuba_H__
#define  __Tuba_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Tuba
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

class TubaSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec9[2];
	
  public:
	
	int getNumInputsTubaSIG0() {
		return 0;
	}
	int getNumOutputsTubaSIG0() {
		return 1;
	}
	
	void instanceInitTubaSIG0(int sample_rate) {
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iVec2[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			iRec9[l9] = 0;
		}
	}
	
	void fillTubaSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec9[0] = (iVec2[1] + iRec9[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec9[0]));
			iVec2[1] = iVec2[0];
			iRec9[1] = iRec9[0];
		}
	}

};

static TubaSIG0* newTubaSIG0() { return (TubaSIG0*)new TubaSIG0(); }
static void deleteTubaSIG0(TubaSIG0* dsp) { delete dsp; }

static float Tuba_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0TubaSIG0[65536];

class Tuba : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst6;
	float fConst7;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	float fRec1[2];
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec2[2];
	float fConst11;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst12;
	float fConst14;
	float fConst16;
	float fConst17;
	int iRec5[2];
	float fConst18;
	float fConst19;
	float fConst20;
	int iRec6[2];
	FAUSTFLOAT fHslider2;
	float fRec4[3];
	FAUSTFLOAT fHslider3;
	float fConst21;
	float fConst22;
	float fConst23;
	FAUSTFLOAT fHslider4;
	float fConst24;
	float fRec7[2];
	float fRec10[2];
	float fRec3[3];
	float fRec0[3];
	float fConst26;
	float fConst27;
	
 public:
	Tuba() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Tuba -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "tuba.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/peak_eq:author", "Julius O. Smith III");
		m->declare("filters.lib/peak_eq:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/peak_eq:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "tuba");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		TubaSIG0* sig0 = newTubaSIG0();
		sig0->instanceInitTubaSIG0(sample_rate);
		sig0->fillTubaSIG0(65536, ftbl0TubaSIG0);
		deleteTubaSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(989.6017f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / Tuba_faustpower2_f(fConst1));
		float fConst3 = fConst0 * std::sin(1979.2034f / fConst0);
		float fConst4 = 816.8141f / fConst3;
		float fConst5 = 1.0f / fConst1;
		fConst6 = (fConst5 - fConst4) / fConst1 + 1.0f;
		fConst7 = 1.0f / ((fConst5 + fConst4) / fConst1 + 1.0f);
		fConst8 = std::max<float>(1.0f, 0.012f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 0.4f / std::max<float>(1.0f, 0.16f * fConst0);
		fConst11 = 1.0f / std::max<float>(1.0f, 0.12f * fConst0);
		fConst12 = 3.1415927f / fConst0;
		float fConst13 = std::tan(2199.1147f / fConst0);
		fConst14 = 2.0f * (1.0f - 1.0f / Tuba_faustpower2_f(fConst13));
		float fConst15 = 1.0f / fConst13;
		fConst16 = (fConst15 + -1.4142135f) / fConst13 + 1.0f;
		fConst17 = 1.0f / ((fConst15 + 1.4142135f) / fConst13 + 1.0f);
		fConst18 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst19 = 1.0f / fConst18;
		fConst20 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst21 = 0.18f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst22 = 1.0f / std::max<float>(1.0f, 0.06f * fConst0);
		fConst23 = 1.0f / std::max<float>(1.0f, 0.08f * fConst0);
		fConst24 = 1.0f / fConst0;
		float fConst25 = 1294.5631f / fConst3;
		fConst26 = (fConst5 - fConst25) / fConst1 + 1.0f;
		fConst27 = (fConst5 + fConst25) / fConst1 + 1.0f;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.45f);
		fHslider1 = FAUSTFLOAT(0.6f);
		fHslider2 = FAUSTFLOAT(0.4f);
		fHslider3 = FAUSTFLOAT(0.015f);
		fHslider4 = FAUSTFLOAT(82.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec2[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec5[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec6[l5] = 0;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec7[l7] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec10[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec3[l11] = 0.0f;
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
	
	virtual Tuba* clone() {
		return new Tuba();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("tuba");
		ui_interface->addHorizontalSlider("attack", &fHslider3, FAUSTFLOAT(0.015f), FAUSTFLOAT(0.004f), FAUSTFLOAT(0.15f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bark", &fHslider0, FAUSTFLOAT(0.45f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("breath", &fHslider2, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(82.0f), FAUSTFLOAT(25.0f), FAUSTFLOAT(4e+02f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider1, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.5e+03f * float(fHslider0) + 2e+02f;
		float fSlow3 = float(fHslider1);
		float fSlow4 = 0.4f * fSlow3 + 0.6f;
		float fSlow5 = 2.3283065e-11f * float(fHslider2);
		float fSlow6 = std::max<float>(1.0f, fConst0 * float(fHslider3));
		float fSlow7 = 1.0f / fSlow6;
		float fSlow8 = float(fHslider4);
		float fSlow9 = fConst24 * fSlow8;
		float fSlow10 = 0.85f * fSlow3;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			float fTemp0 = fConst2 * fRec0[1];
			fVec1[0] = fSlow0;
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			iRec2[0] = iSlow1 * (iRec2[1] + 1);
			float fTemp1 = float(iRec2[0]);
			float fTemp2 = 1.0f - fConst11 * fTemp1;
			float fTemp3 = std::tan(fConst12 * std::min<float>(fSlow4 * (fSlow2 * std::max<float>(0.0f, fTemp2 * std::min<float>(fConst9 * fRec1[0], std::max<float>(fConst10 * (fConst8 - fRec1[0]) + 1.0f, 0.6f))) + 1.6e+02f), 8e+03f));
			float fTemp4 = 1.0f / fTemp3;
			float fTemp5 = (fTemp4 + 0.95238096f) / fTemp3 + 1.0f;
			iRec5[0] = (iRec5[1] + (iRec5[1] > 0)) * (fSlow0 <= fVec1[1]) + (fSlow0 > fVec1[1]);
			float fTemp6 = float(iRec5[0]);
			iRec6[0] = 1103515245 * iRec6[1] + 12345;
			fRec4[0] = fSlow5 * float(iRec6[0]) * std::max<float>(0.0f, std::min<float>(fConst19 * fTemp6, fConst20 * (fConst18 - fTemp6) + 1.0f)) - fConst17 * (fConst16 * fRec4[2] + fConst14 * fRec4[1]);
			float fTemp7 = std::max<float>(0.0f, std::min<float>(fSlow7 * fRec1[0], std::max<float>(fConst21 * (fSlow6 - fRec1[0]) + 1.0f, 0.82f)) * fTemp2);
			float fTemp8 = 0.03f * std::max<float>(0.0f, std::min<float>(fConst23 * fRec1[0], 1.0f) - fConst22 * fTemp1) + 0.97f;
			float fTemp9 = std::max<float>(1.1920929e-07f, std::fabs(fSlow8 * fTemp8));
			float fTemp10 = fRec7[1] + fConst24 * fTemp9;
			float fTemp11 = fTemp10 + -1.0f;
			int iTemp12 = fTemp11 < 0.0f;
			fRec7[0] = ((iTemp12) ? fTemp10 : fTemp11);
			float fRec8 = ((iTemp12) ? fTemp10 : fTemp10 + fTemp11 * (1.0f - fConst0 / fTemp9));
			float fTemp13 = ((1 - iVec0[1]) ? 0.0f : fRec10[1] + fSlow9 * fTemp8);
			fRec10[0] = fTemp13 - std::floor(fTemp13);
			fRec3[0] = fSlow10 * (fTemp7 * (0.52f * ftbl0TubaSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))] + 0.48f * (2.0f * fRec8 + -1.0f) * fTemp7) + fConst17 * (fRec4[2] + fRec4[0] + 2.0f * fRec4[1])) - (fRec3[2] * ((fTemp4 + -0.95238096f) / fTemp3 + 1.0f) + 2.0f * fRec3[1] * (1.0f - 1.0f / Tuba_faustpower2_f(fTemp3))) / fTemp5;
			fRec0[0] = (fRec3[2] + fRec3[0] + 2.0f * fRec3[1]) / fTemp5 - fConst7 * (fConst6 * fRec0[2] + fTemp0);
			float fTemp14 = fConst7 * (fTemp0 + fConst27 * fRec0[0] + fConst26 * fRec0[2]);
			output0[i0] = FAUSTFLOAT(fTemp14);
			output1[i0] = FAUSTFLOAT(fTemp14);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			fRec1[1] = fRec1[0];
			iRec2[1] = iRec2[0];
			iRec5[1] = iRec5[0];
			iRec6[1] = iRec6[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec7[1] = fRec7[0];
			fRec10[1] = fRec10[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
