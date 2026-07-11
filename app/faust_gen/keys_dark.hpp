/* ------------------------------------------------------------
name: "keys_dark"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn KeysDark -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __KeysDark_H__
#define  __KeysDark_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS KeysDark
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

class KeysDarkSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec3[2];
	
  public:
	
	int getNumInputsKeysDarkSIG0() {
		return 0;
	}
	int getNumOutputsKeysDarkSIG0() {
		return 1;
	}
	
	void instanceInitKeysDarkSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec3[l5] = 0;
		}
	}
	
	void fillKeysDarkSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec3[0] = (iVec2[1] + iRec3[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec3[0]));
			iVec2[1] = iVec2[0];
			iRec3[1] = iRec3[0];
		}
	}

};

static KeysDarkSIG0* newKeysDarkSIG0() { return (KeysDarkSIG0*)new KeysDarkSIG0(); }
static void deleteKeysDarkSIG0(KeysDarkSIG0* dsp) { delete dsp; }

static float KeysDark_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0KeysDarkSIG0[65536];

class KeysDark : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst1;
	float fRec1[2];
	float fConst2;
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst5;
	float fConst6;
	float fConst7;
	float fConst8;
	float fConst9;
	float fConst10;
	FAUSTFLOAT fHslider2;
	float fConst11;
	float fRec4[2];
	FAUSTFLOAT fHslider3;
	float fConst12;
	float fConst13;
	float fConst14;
	float fRec6[2];
	FAUSTFLOAT fHslider4;
	FAUSTFLOAT fHslider5;
	float fConst15;
	float fRec7[2];
	float fVec3[2];
	int IOTA0;
	float fVec4[4096];
	float fConst16;
	float fRec5[2];
	float fRec9[2];
	float fVec5[2];
	float fVec6[4096];
	float fRec8[2];
	float fConst17;
	float fRec2[3];
	FAUSTFLOAT fHslider6;
	
 public:
	KeysDark() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn KeysDark -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "keys_dark.dsp");
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
		m->declare("filters.lib/pole:author", "Julius O. Smith III");
		m->declare("filters.lib/pole:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/pole:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "keys_dark");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
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
		KeysDarkSIG0* sig0 = newKeysDarkSIG0();
		sig0->instanceInitKeysDarkSIG0(sample_rate);
		sig0->fillKeysDarkSIG0(65536, ftbl0KeysDarkSIG0);
		deleteKeysDarkSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.4f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.01f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 0.7f / std::max<float>(1.0f, 0.7f * fConst0);
		fConst5 = 3.1415927f / fConst0;
		fConst6 = 1.0f / std::max<float>(1.0f, 0.35f * fConst0);
		fConst7 = std::max<float>(1.0f, 0.006f * fConst0);
		fConst8 = 1.0f / fConst7;
		fConst9 = 0.5f * fConst0;
		fConst10 = 0.45f / std::max<float>(1.0f, fConst9);
		fConst11 = 0.5f / fConst0;
		fConst12 = 1.0f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst13 = 1.0f / std::max<float>(1.0f, 0.6f * fConst0);
		fConst14 = 5.0f / fConst0;
		fConst15 = 1.0f / fConst0;
		fConst16 = 0.25f * fConst0;
		fConst17 = 4.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(2.6e+03f);
		fHslider1 = FAUSTFLOAT(7e+02f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fHslider3 = FAUSTFLOAT(0.5f);
		fHslider4 = FAUSTFLOAT(0.004f);
		fHslider5 = FAUSTFLOAT(0.004f);
		fHslider6 = FAUSTFLOAT(0.65f);
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
			fRec6[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fVec3[l9] = 0.0f;
		}
		IOTA0 = 0;
		for (int l10 = 0; l10 < 4096; l10 = l10 + 1) {
			fVec4[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec5[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec9[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fVec5[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 4096; l14 = l14 + 1) {
			fVec6[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec8[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 3; l16 = l16 + 1) {
			fRec2[l16] = 0.0f;
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
	
	virtual KeysDark* clone() {
		return new KeysDark();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("keys_dark");
		ui_interface->addHorizontalSlider("cutoff", &fHslider1, FAUSTFLOAT(7e+02f), FAUSTFLOAT(2e+02f), FAUSTFLOAT(3e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("detune", &fHslider5, FAUSTFLOAT(0.004f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.02f), FAUSTFLOAT(0.0005f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(3e+01f), FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider6, FAUSTFLOAT(0.65f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sub", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("sweep", &fHslider0, FAUSTFLOAT(2.6e+03f), FAUSTFLOAT(0.0f), FAUSTFLOAT(6e+03f), FAUSTFLOAT(1e+01f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider4, FAUSTFLOAT(0.004f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.02f), FAUSTFLOAT(0.0005f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = float(fHslider0);
		float fSlow3 = float(fHslider1);
		float fSlow4 = float(fHslider2);
		float fSlow5 = fConst11 * fSlow4;
		float fSlow6 = float(fHslider3);
		float fSlow7 = float(fHslider4);
		float fSlow8 = float(fHslider5) + 1.0f;
		float fSlow9 = fSlow4 * fSlow8;
		float fSlow10 = fConst17 * fSlow4;
		float fSlow11 = float(fHslider6);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			float fTemp1 = std::tan(fConst5 * (fSlow3 + fSlow2 * std::max<float>(0.0f, std::min<float>(fConst3 * fRec1[0], std::max<float>(fConst4 * (fConst2 - fRec1[0]) + 1.0f, 0.3f)) * (1.0f - fConst1 * fTemp0))));
			float fTemp2 = 1.0f / fTemp1;
			float fTemp3 = (fTemp2 + 1.4142135f) / fTemp1 + 1.0f;
			int iTemp4 = 1 - iVec0[1];
			float fTemp5 = ((iTemp4) ? 0.0f : fSlow5 + fRec4[1]);
			fRec4[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp4) ? 0.0f : fConst14 + fRec6[1]);
			fRec6[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = fSlow7 * ftbl0KeysDarkSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst13 * fRec1[0], 1.0f) - fConst12 * fTemp0) + 1.0f;
			float fTemp8 = std::max<float>(fSlow9 * fTemp7, 23.44895f);
			float fTemp9 = std::max<float>(2e+01f, std::fabs(fTemp8));
			float fTemp10 = ((iTemp4) ? 0.0f : fRec7[1] + fConst15 * fTemp9);
			fRec7[0] = fTemp10 - std::floor(fTemp10);
			float fTemp11 = KeysDark_faustpower2_f(2.0f * fRec7[0] + -1.0f);
			fVec3[0] = fTemp11;
			float fTemp12 = float(iVec0[1]);
			float fTemp13 = fTemp12 * (fTemp11 - fVec3[1]) / fTemp9;
			fVec4[IOTA0 & 4095] = fTemp13;
			float fTemp14 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst9 / fTemp8));
			int iTemp15 = int(fTemp14);
			float fTemp16 = std::floor(fTemp14);
			fRec5[0] = 0.999f * fRec5[1] + fConst16 * (fTemp13 - fVec4[(IOTA0 - iTemp15) & 4095] * (fTemp16 + (1.0f - fTemp14)) - (fTemp14 - fTemp16) * fVec4[(IOTA0 - (iTemp15 + 1)) & 4095]);
			float fTemp17 = std::max<float>(fSlow4 * fTemp7, 23.44895f);
			float fTemp18 = std::max<float>(2e+01f, std::fabs(fTemp17));
			float fTemp19 = ((iTemp4) ? 0.0f : fRec9[1] + fConst15 * fTemp18);
			fRec9[0] = fTemp19 - std::floor(fTemp19);
			float fTemp20 = KeysDark_faustpower2_f(2.0f * fRec9[0] + -1.0f);
			fVec5[0] = fTemp20;
			float fTemp21 = fTemp12 * (fTemp20 - fVec5[1]) / fTemp18;
			fVec6[IOTA0 & 4095] = fTemp21;
			float fTemp22 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst9 / fTemp17));
			int iTemp23 = int(fTemp22);
			float fTemp24 = std::floor(fTemp22);
			fRec8[0] = 0.999f * fRec8[1] + fConst16 * (fTemp21 - fVec6[(IOTA0 - iTemp23) & 4095] * (fTemp24 + (1.0f - fTemp22)) - (fTemp22 - fTemp24) * fVec6[(IOTA0 - (iTemp23 + 1)) & 4095]);
			fRec2[0] = 0.4f * (fSlow10 * fTemp7 * (fRec8[0] + fSlow8 * fRec5[0]) + fSlow6 * ftbl0KeysDarkSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))]) - (fRec2[2] * ((fTemp2 + -1.4142135f) / fTemp1 + 1.0f) + 2.0f * fRec2[1] * (1.0f - 1.0f / KeysDark_faustpower2_f(fTemp1))) / fTemp3;
			float fTemp25 = fSlow11 * ((fRec2[2] + fRec2[0] + 2.0f * fRec2[1]) * std::max<float>(0.0f, std::min<float>(fConst8 * fRec1[0], std::max<float>(fConst10 * (fConst7 - fRec1[0]) + 1.0f, 0.55f)) * (1.0f - fConst6 * fTemp0)) / fTemp3);
			output0[i0] = FAUSTFLOAT(fTemp25);
			output1[i0] = FAUSTFLOAT(fTemp25);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec4[1] = fRec4[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fVec3[1] = fVec3[0];
			IOTA0 = IOTA0 + 1;
			fRec5[1] = fRec5[0];
			fRec9[1] = fRec9[0];
			fVec5[1] = fVec5[0];
			fRec8[1] = fRec8[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
